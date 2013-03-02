import csv
import datetime
import time
import StringIO


import requests
from lxml import etree
from pymongo import MongoClient


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
        url = cls.CATEGORY_URL + "/Top/" + category.replace(" ", "_")
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
    def wait_until_running(cls, r):
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
    def fetch_stats(cls, r):
        """Fetch test results in csv format and convert them to dictionary"""
        url = r.json()["data"]["summaryCSV"]
        try:
            summary_csv = requests.get(url).text
            csv_reader = csv.reader(StringIO.StringIO(summary_csv),
                                    delimiter=',')
            header = csv_reader.next()
            data = csv_reader.next()
        except UnicodeEncodeError:
            return {}
        else:
            return dict((key, data[index]) for index, key in enumerate(header))

    @classmethod
    def test(cls, url):
        """Run test for given URL and return dictionary with stats"""
        cls.TESTCONFIG["url"] = url
        r = requests.get(cls.RUN_API, params=cls.TESTCONFIG)
        cls.wait_until_running(r)
        return cls.fetch_stats(r)


class Crawler():

    def __init__(self):
        connection = MongoClient()
        self.collection = connection.bportal.benchmarks

    def update(self, category, title, link, stats):
        avg_load_time = float(stats["Activity Time(ms)"]) / 1000
        self.collection.update(
            {"categoty": category, "title": title},
            {"$set": {"status": "obsolete"}}
        )
        self.collection.insert({
            "category": category,
            "title": title,
            "timestamp": datetime.datetime.utcnow(),
            "uri": "http://" + link,
            "avg_load_time": '{0:.1f}'.format(avg_load_time),
            "status": "recent"
        })

    def crawl(self):
        for category in AlexaParser.get_categories():
            for title, link in AlexaParser.get_websites(category):
                stats = WebPagetest.test(link)
                if stats:
                    self.update(category, title, link, stats)


def main():
    crawler = Crawler()
    while True:
        crawler.crawl()

if __name__ == "__main__":
    main()
