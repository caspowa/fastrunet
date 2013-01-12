import requests
from lxml import etree


class AlexaParser(object):

    CATEGORY_URL = "http://www.alexa.com/topsites/category"

    def get_categories(self):
        html = requests.get(self.CATEGORY_URL).text
        tree = etree.HTML(html)
        for ul in tree.xpath("//*[@id=\"topsites-category\"]/div[1]/div/ul"):
            for li in ul.xpath("li"):
                for a in li.xpath("a"):
                    yield a.text.strip()
