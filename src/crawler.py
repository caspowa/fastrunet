import csv
import datetime
import time
import io

import requests
from lxml import etree
from pymongo import MongoClient

from logger import logger


class YandexParser(object):

    BASE_URL = "http://yaca.yandex.ru/"

    CATEGORIES = {
        "Развлечения": "/yca/ungrp/cat/Entertainment/",
        "Hi-Tech": "/yca/ungrp/cat/Computers/",
        "Авто": "/yca/ungrp/cat/Automobiles/",
        "Бизнес": "/yca/ungrp/cat/Business/",
        "Отдых": "/yca/ungrp/cat/Rest/",
        "Спорт": "/yca/ungrp/cat/Sports/",
        "СМИ": "/yca/ungrp/cat/Media/",
        "Порталы": "/yca/ungrp/cat/Portals/",
        "Дом": "/yca/ungrp/cat/Private_Life/",
        "Работа": "/yca/ungrp/cat/Employment/",
        "Учёба": "/yca/ungrp/cat/Science/",
        "Справки": "/yca/ungrp/cat/Reference/",
        "Общество": "/yca/ungrp/cat/Society/",
        "Культура": "/yca/ungrp/cat/Culture/",
        "Производство": "/yca/ungrp/cat/Business/Production/",
    }

    @classmethod
    def get_categories(cls):
        """Yield website categories"""
        html = requests.get(cls.BASE_URL).text
        tree = etree.HTML(html)
        for div1 in tree.xpath("/html/body/table[2]/tr/td[2]/div/div"):
            for div2 in div1.xpath("div"):
                for a in div2.xpath("dl/dt/a[2]"):
                    print(a.text.strip())

    @classmethod
    def get_websites(cls, href):
        for page in range(2):
            url = "{0}{1}{2}.html".format(cls.BASE_URL, href, page)
            html = requests.get(url).text
            tree = etree.HTML(html)
            for li in tree.xpath("/html/body/table[4]/tr/td[2]/ol/li"):
                text = li.xpath("h3/a[1]")[0].text
                link = li.xpath("h3/a[1]/@href")[0]
                yield text, link


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
            csv_reader = csv.reader(io.StringIO(summary_csv), delimiter=",")
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
        self.collection = connection.fastrunet.benchmarks

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
            "avg_load_time": "{0:.1f}".format(load_time),
            "status": "recent",
            "rank": rank
        })
        logger.info("Successfully updated results for: {0}".format(link))

    def _crawl(self):
        for category, href in YandexParser.CATEGORIES.items():
            websites = YandexParser.get_websites(href)
            for rank, (title, link) in enumerate(websites, start=1):
                test_results = [test for test in (WebPagetest.test(link)
                                                  for _ in range(3)) if test]
                if test_results:
                    median = test_results[round(len(test_results) / 2)]
                    load_time = float(median["Activity Time(ms)"]) / 1000.0
                    self._update(category, rank, title, link, load_time)

    def run(self):
        while True:
            self._crawl()


def main():
    crawler = Crawler()
    crawler.run()

if __name__ == "__main__":
    main()
