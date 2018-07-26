#VERSION: 0.3
#AUTHORS: nindogo

import re
import threading
import time
from html.parser import HTMLParser

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
URL = 'https://yourbittorrent.com'


class parse_desc_links(HTMLParser):
    A, TD, TR, HREF, TABLE, DIV, INPUT, BODY = (
        'a', 'td', 'tr', 'href', 'table', 'div', 'input', 'body')
    inHREFCELL = False
    the_results = []

    def handle_starttag(self, tag, attrs):
        this_tag = tag
        params = dict(attrs)
        if this_tag == self.TD and (params.get('class') == 'v' or params.get('class') == 'n'):
            self.inHREFCELL = True
        if this_tag == self.A and params.get('href') and self.inHREFCELL:
            working_url = params.get('href')
            if re.match(r'^/torrent', working_url):
                desc_link = URL + params.get('href')
                self.the_results.append(desc_link)


class yourbittorrent(object):
    url = 'https://yourbittorrent.com'
    name = 'YourBittorrent'
    supported_categories = {
        'all':''
        ,'movies':'1'
        ,'tv':'3'
        ,'games':'4'
        ,'music':'2'
        ,'anime':'6'
        ,'software':'5'
        ,'books':'8'
        ,'adult':'7'
    }

    GET_NUM_RESULTS = re.compile(r'<\/b> of <b>(\d*)<\/b> torrents found for "')
    TRACKERS = (r'&tr=http%3a%2f%2ftracker.trackerfix.com%3a80%2fannounce&tr=udp%3a%2f%2f9.rarbg.to%3a2710%2fannounce&tr=udp%3a%2f%2fcoppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2feddie4.nl%3a6969%2fannounce&tr=udp%3a%2f%2fexodus.desync.com%3a6969&tr=udp%3a%2f%2fglotorrents.pw%3a6969%2fannounce&tr=udp%3a%2f%2fopen.demonii.com%3a1337&tr=udp%3a%2f%2fp4p.arenabg.ch%3a1337%2fannounce&tr=udp%3a%2f%2ftorrent.gresille.org%3a80%2fannounce&tr=udp%3a%2f%2ftracker.aletorrenty.pl%3a2710%2fannounce&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.glotorrents.com%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.internetwarriors.net%3a1337&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fzer0day.ch%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.pirateparty.gr%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.open-internet.nl%3a6969%2fannounce&tr=%20udp%3a%2f%2fmgtracker.org%3a6969%2fannounce')
    GET_SIZE_RE = (r'<\/b><\/td><\/tr><\/thead><tr><td width=120px><b>Size<\/td><td>(.+)\sin\s\d+\sfiles?') # Not the best regex
    GET_NAME_RE = re.compile(r'<!DOCTYPE html><html lang="en-US"><head><title>(.*)Torrent Download</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1')
    GET_SEED_LEECH_HASH = re.compile(r'</td></tr><tr><td><b>Status</td><td><font color=green>(.*)</font> seeds & <font color="#2E0854">(.*)</font> peers. </td></tr><tr><td><b>Hash</td><td>(.*)</td></tr><tr><td valign=top><b>Rating</td>')
    
    def find_results(self, desc_link):
        this_result = {}
        this_result.clear()
        this_result['desc_link'] = desc_link
        results_page = retrieve_url(desc_link)

        this_result['engine_url'] = URL
        this_result['name'] = str(re.findall(self.GET_NAME_RE, results_page)[0]).replace('|', '')
        this_result['seeds'], this_result['leech'], thisHash = re.findall(self.GET_SEED_LEECH_HASH, results_page)[0]
        this_result['link'] = 'magnet:?xt=urn:btih:' + thisHash + '&dn=' + this_result['name'] + self.TRACKERS
        this_result['size'] = str(re.findall(self.GET_SIZE_RE, results_page)[0])

        prettyPrinter(this_result)
        this_result.clear()
        quit()
        pass

    def search(self, what, cat='all'):
        query = str(what).replace(r' ', '+')
        page, total_records, curr_record = 1, 0, 0
        find_desc_link = parse_desc_links()
        while (int(total_records) >= curr_record) and (page <= 21):
            curr_query = "https://yourbittorrent.com/?q=" + query + '&c=' + self.supported_categories[cat.lower()] + '&page=' + str(page)
            curr_page = retrieve_url(curr_query)
            try:
                total_records = re.findall(self.GET_NUM_RESULTS, curr_page)[0]
            except IndexError:
                quit()
       
            find_desc_link.feed(curr_page)
            for link in find_desc_link.the_results:
                curr_record += 1
                t = threading.Thread(target=self.find_results, args=(link,))
                t.start()
                t.join()
            page += 1
            find_desc_link.the_results.clear()
        pass


if __name__ == '__main__':
    a = yourbittorrent()
    a.search('ncis')
