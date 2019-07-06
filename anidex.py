# VERSION: 0.02
# AUTHORS: nindogo (nindogo@gmail.com)

# LICENSING INFORMATION

import re
import time
import threading
try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser

from helpers import retrieve_url
from novaprinter import prettyPrinter


class anidex(object):
    url = 'https://anidex.info/'
    name = 'AniDex'
    supported_categories = {
        'all': '',
        'music': 'id=9,10,11&',
        'games': 'id=12&',
        'anime': 'id=1,2,3&',
        'software': 'id=13&',
        'pictures': 'id=14&',
        'books': 'id=6,7,8&',
    }

    class anidexParser(HTMLParser):
        url = 'https://anidex.info'
        TR, TH, TD, A, SPAN = 'tr', 'th', 'td', 'a', 'span'
        inRow = False
        getSize = False
        getSeed = False
        getLeech = False
        this_result = {}

        def handle_starttag(self, tag, attrs):
            if tag == self.TR and self.inRow is False:
                self.inRow = True
            if tag == self.TH and self.inRow is True:
                self.inRow = False
            if self.inRow is True and tag == self.TD:
                my_attrs = dict(attrs)
                if my_attrs.get('class') == 'text-center td-992' and my_attrs.get('title') is None:
                    self.getSize = True
                if my_attrs.get('class') == 'text-success text-right':
                    self.getSeed = True
                if my_attrs.get('class') == 'text-danger text-right':
                    self.getLeech = True
            if self.inRow and tag == self.A:
                my_attrs = dict(attrs)
                if my_attrs.get('href').startswith('magnet'):
                    self.this_result['link'] = my_attrs.get('href')
                if my_attrs.get('class') == 'torrent':
                    self.this_result['desc_link'] = self.url + my_attrs.get('href')
            if self.inRow and tag == self.SPAN:
                my_attrs = dict(attrs)
                if my_attrs.get('class') == 'span-1440':
                    self.this_result['name'] = my_attrs.get('title')

        def handle_endtag(self, tag):
            if self.inRow is True and tag == self.TR:
                self.inRow = False
                self.this_result['engine_url'] = self.url
                prettyPrinter(self.this_result)

        def handle_data(self, data):
            if self.inRow and self.getSize:
                self.this_result['size'] = data.strip().replace(',', '')
                self.getSize = False
            if self.inRow and self.getSeed:
                self.this_result['seeds'] = data.strip().replace(',', '')
                self.getSeed = False
            if self.inRow and self.getLeech:
                self.this_result['leech'] = data.strip().replace(',', '')
                self.getLeech = False

    def do_search(self, url):
        webpage = retrieve_url(url)
        adexParser = self.anidexParser()
        adexParser.feed(webpage)

    def search(self, what, cat='all'):
        query = str(what).replace(' ', '+')
        search_url = self.url + \
            '?s=seeders&o=desc&' + \
            self.supported_categories[cat.lower()] + \
            'q=' + query

        webpage = retrieve_url(search_url)
        total_results = re.findall(r'Showing[^f]+f(.+?)torrents', webpage)[0].strip().replace(',', '')
        total_results = int(total_results)

        adexParser = self.anidexParser()
        adexParser.feed(webpage)

        threads = []
        for offset in range(50, total_results, 50):
            this_url = search_url + '&offset=' + str(offset)
            t = threading.Thread(args=(this_url,), target=self.do_search)
            time.sleep(2)
            t.start()
            threads.append(t)
            # self.do_search(this_url)

        for t in threads:
            t.join()


if __name__ == '__main__':
    a = anidex()
    a.search('DS', 'all')
