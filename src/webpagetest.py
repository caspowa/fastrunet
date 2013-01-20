import time
import StringIO
import csv

import requests

from alexa_parser import AlexaParser


class WebPagetest(object):

    RUN_API = "http://www.webpagetest.org/runtest.php"
    STATUS_API = "http://www.webpagetest.org/testStatus.php"
    TESTCONFIG = {
        "location": "Dulles:Chrome",  # TODO: self managed instance
        "private": 1,
        "f": "json",
        "k": "8e3c759f8a1848c396bc7ccabb0d1a07",
        "fvonly": 1
    }

    def __int__(self):
        self.parser = AlexaParser()

    def wait_until_running(self, r):
        """Wait until test in pending or running state"""
        params = {"test": r.json()["data"]["testId"]}
        while True:
            try:
                r = requests.get(url=self.STATUS_API, params=params)
                if r.json()["statusCode"] == 200:
                    break
                else:
                    time.sleep(5)
            except requests.exceptions.ConnectionError:
                time.sleep(10)

    def fetch_stats(self, r):
        """Fetch test results in csv format and convert them to dictionary"""
        url = r.json()["data"]["summaryCSV"]
        summary_csv = requests.get(url).text
        csv_reader = csv.reader(StringIO.StringIO(summary_csv), delimiter=',')
        header = csv_reader.next()
        data = csv_reader.next()
        return dict((key, data[index]) for index, key in enumerate(header))

    def run(self, url):
        """Run test for given URL and return dictionary with stats"""
        self.TESTCONFIG["url"] = url
        r = requests.get(self.RUN_API, params=self.TESTCONFIG)
        self.wait_until_running(r)
        return self.fetch_stats(r)
