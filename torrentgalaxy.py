# VERSION: 0.08
# AUTHORS: nindogo (nindogo@gmail.com)

# LICENSING INFORMATION

import re
import math
import http.cookiejar
import time
import urllib.request
import urllib.parse
import random
import string
import threading
from helpers import retrieve_url
from novaprinter import prettyPrinter
# some other imports if necessary
try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser


class torrentgalaxy(object):
    url = 'https://torrentgalaxy.to/'
    name = 'TorrentGalaxy'
    supported_categories = {
        'all': '',
        'movies': 'c3=1&c46=1&c45=1&c42=1&c4=1&c1=1&',
        'tv': 'c41=1&c5=1&c6=1&c7=1&',
        'music': 'c23=1&c24=1&c25=1&c26=1&c17=1&',
        'games': 'c43=1&c10=1&',
        'anime': 'c28=1&',
        'software': 'c20=1&c21=1&c18=1&',
        'pictures': 'c37=1&',
        'books': 'c13=1&c19=1&c12=1&c14=1&c15=1&',
    }

    class TorrentGalaxyParser(HTMLParser):
        DIV, A, SPAN, FONT, SMALL, = 'div', 'a', 'span', 'font', 'small'
        count_div, = -1,
        get_size, get_seeds, get_leechs = False, False, False
        this_record = {}
        url = 'https://torrentgalaxy.to'

        def handle_starttag(self, tag, attrs):
            if tag == self.DIV:
                my_attrs = dict(attrs)
                # if (my_attrs.get('class') == 'tgxtablerow txlight'):
                if  my_attrs.get('class') and 'tgxtablerow' in my_attrs.get('class'):
                    self.count_div = 0
                    self.this_record = {}
                    self.this_record['engine_url'] = self.url
                if  my_attrs.get('class') and ('tgxtablecell' in my_attrs.get('class')) and self.count_div >= 0:
                    self.count_div += 1

            if tag == self.A and self.count_div < 13:
                my_attrs = dict(attrs)
                if 'title' in my_attrs and ('class' in my_attrs) and 'txlight' in my_attrs.get('class') and not my_attrs.get('id'):
                    self.this_record['name'] = my_attrs['title']
                    self.this_record['desc_link'] = \
                        self.url + my_attrs['href']
                if 'role' in my_attrs and my_attrs.get('role') == 'button':
                    self.this_record['link'] = my_attrs['href']

            if tag == self.SPAN:
                my_attrs = dict(attrs)
                if 'class' in my_attrs and 'badge badge-secondary' in my_attrs.get('class'):
                    self.get_size = True

            if tag == self.FONT:
                my_attrs = dict(attrs)
                if my_attrs.get('color') == 'green':
                    self.get_seeds = True
                elif my_attrs.get('color') == '#ff0000':
                    self.get_leechs = True

            if self.count_div == 13 and tag == self.SMALL:
                prettyPrinter(self.this_record)
                self.this_record = {}
                self.count_div = -1

        def handle_data(self, data):
            if self.get_size is True and self.count_div < 13:
                self.this_record['size'] = data.strip().replace(',', '')
                self.get_size = False
            if self.get_seeds is True:
                self.this_record['seeds'] = data.strip().replace(',', '')
                self.get_seeds = False
            if self.get_leechs is True:
                self.this_record['leech'] = data.strip().replace(',', '')
                self.get_leechs = False

    def do_search(self, url):
        webpage = retrieve_url(url)
        tgParser = self.TorrentGalaxyParser()
        tgParser.feed(webpage)

    def search(self, what, cat='all'):
        query = str(what).replace(r' ', '+')
        search_url = 'https://torrentgalaxy.to/torrents.php?'
        full_url = \
            search_url + \
            self.supported_categories[cat.lower()] + \
            'sort=seeders&order=desc&search=' + \
            query

        opener = self.init_opener(full_url)
        response = opener.open(full_url)
        webpage = response.read().decode('ISO-8859-1')
        tgParser = self.TorrentGalaxyParser()
        tgParser.feed(webpage)

        # Return early bc I don't want to spam their server with my hacked script
        return

        all_results_re = re.compile(r'steelblue[^>]+>(.*?)<')
        all_results = all_results_re.findall(webpage)[0]
        all_results = all_results.replace(' ', '')
        pages = math.ceil(int(all_results) / 50)
        threads = []
        for page in range(1, pages):
            this_url = full_url + '&page=' + str(page)
            t = threading.Thread(args=(this_url,), target=self.do_search)
            threads.append(t)
            t.start()
            # self.do_search(this_url)
        
        for thread in threads:
            thread.join()

    def init_opener(self, full_url):
        # New browser comes in
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        opener.open(full_url)

        # Wait 5s to generate our "browser fingerprint" and send it off
        time.sleep(5)

        hex_length = 32
        random_hex = ''.join(random.choices(string.hexdigits.lower(), k=hex_length))
        post_data = urllib.parse.urlencode({'fash': random_hex}).encode()
        post_url = "https://torrentgalaxy.to/hub.php?a=vlad&u=" + str((int)(time.time() * 1000))
        post_request = urllib.request.Request(post_url, data=post_data)
        opener.open(post_request)

        # Our opener is ready to go
        return opener


if __name__ == '__main__':
    a = torrentgalaxy()
    a.search('ncis new', 'all')
