import csv
import datetime
import time
import io

import requests
from lxml import etree
from daemon import runner
from pymongo import MongoClient

from logger import logger


class AlexaParser(object):

    CATEGORY_URL = "http://www.alexa.com/topsites/category"

    @classmethod
    def get_categories(cls):
        """Yield website categories"""
        html = requests.get(cls.CATEGORY_URL).text
        tree = etree.HTML(html)
        for ul in tree.xpath("//*[@id=\"topsites-category\"]/div[1]/div/ul"):
            for li in ul.xpath("li"):
                for a in li.xpath("a"):
                    yield a.text.strip()

    @classmethod
    def get_websites(cls, category):
        """Yield website titles and URLs as tuple"""
        category = category.replace(" ", "_")
        for page in range(2):
            url = cls.CATEGORY_URL + ";{0}/Top/".format(page) + category
            html = requests.get(url).text
            tree = etree.HTML(html)
            for li in tree.xpath("//*[@id=\"topsites-category\"]/ul/li"):
                title = li.xpath("div[2]/h2/a")[0].text.strip()
                link = li.xpath("div[2]/span")[0].text.strip()
                yield title, link


class WebPagetest(object):

    RUN_API = "http://webpagetest.caspowa.com/runtest.php"
    STATUS_API = "http://webpagetest.caspowa.com/testStatus.php"
    TESTCONFIG = {"private": 1, "f": "json", "fvonly": 1}

    @classmethod
    def _wait_until_running(cls, r):
        """Wait until test in pending or running state"""
        params = {"test": r.json()["data"]["testId"]}
        while True:
            try:
                r = requests.get(url=cls.STATUS_API, params=params)
                if r.json()["statusCode"] == 200:
                    break
                else:
                    time.sleep(5)
            except requests.exceptions.ConnectionError:
                time.sleep(10)

    @classmethod
    def _fetch_stats(cls, r):
        """Fetch test results in csv format and convert them to dictionary"""
        url = r.json()["data"]["summaryCSV"]
        try:
            summary_csv = requests.get(url).text
            csv_reader = csv.reader(io.StringIO(summary_csv), delimiter=',')
            header = next(csv_reader)
            data = next(csv_reader)
        except (UnicodeEncodeError, StopIteration):
            return {}
        else:
            return dict((key, data[index]) for index, key in enumerate(header))

    @classmethod
    def test(cls, url):
        """Run test for given URL and return dictionary with stats"""
        logger.info("Running test for: {0}".format(url))

        cls.TESTCONFIG["url"] = url
        r = requests.get(cls.RUN_API, params=cls.TESTCONFIG)
        cls._wait_until_running(r)
        return cls._fetch_stats(r)


class Daemon(object):

    def __init__(self):
        self.stdin_path = "/dev/null"
        self.stdout_path = "/dev/null"
        self.stderr_path = "/dev/null"
        self.pidfile_path = "/tmp/crawler.pid"
        self.pidfile_timeout = 5


class Crawler(Daemon):

    def __init__(self):
        super(Crawler, self).__init__()
        connection = MongoClient()
        self.collection = connection.bportal.benchmarks

    def _update(self, category, rank, title, link, load_time):
        self.collection.update(
            {"category": category, "$or": [{"uri": "http://" + link},
                                           {"rank": rank}]},
            {"$set": {"status": "obsolete"}},
            multi=True
        )
        self.collection.insert({
            "category": category,
            "title": title,
            "timestamp": datetime.datetime.utcnow(),
            "uri": "http://" + link,
            "avg_load_time": '{0:.1f}'.format(load_time),
            "status": "recent",
            "rank": rank
        })
        logger.info("Successfully updated results for: {0}".format(link))

    def _crawl(self):
        for category in AlexaParser.get_categories():
            websites = AlexaParser.get_websites(category)
            for rank, (title, link) in enumerate(websites, start=1):
                test_results = [test for test in (WebPagetest.test(link)
                                                  for _ in range(3)) if test]
                if test_results:
                    median = test_results[len(test_results) / 2]
                    load_time = float(median["Activity Time(ms)"]) / 1000.0
                    self._update(category, rank, title, link, load_time)

    def run(self):
        while True:
            self._crawl()


def main():
    crawler = Crawler()
    daemon_runner = runner.DaemonRunner(crawler)
    daemon_runner.daemon_context.files_preserve = [logger.handlers[0].stream]
    try:
        daemon_runner.do_action()
    except runner.DaemonRunnerStopFailureError:
        pass

if __name__ == "__main__":
    main()
