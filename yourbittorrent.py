#VERSION: 0.2
#AUTHORS: nindogo

import re
from html.parser import HTMLParser

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
URL = 'https://yourbittorrent.com'

the_results = []

class yourBitParser(HTMLParser):
    A, TD, TR, HREF, TABLE, DIV, INPUT, BODY = (
         'a', 'td', 'tr', 'href', 'table', 'div', 'input', 'body')
    GET_NUM_RESULTS = re.compile(r'<\/b> of <b>(\d*)<\/b> torrents found for "')
    GET_NAME_RE = re.compile(r'<!DOCTYPE html><html lang="en-US"><head><title>(.*)Torrent Download</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1')
    GET_HASH_RE = re.compile(r'<\/td><\/tr><tr><td><b>Hash<\/td><td>(.*)<\/td><\/tr><tr><td valign=top><b>Rating<\/td><td id="')
    TRACKERS = (r'&tr=http%3a%2f%2ftracker.trackerfix.com%3a80%2fannounce&tr=udp%3a%2f%2f9.rarbg.to%3a2710%2fannounce&tr=udp%3a%2f%2fcoppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2feddie4.nl%3a6969%2fannounce&tr=udp%3a%2f%2fexodus.desync.com%3a6969&tr=udp%3a%2f%2fglotorrents.pw%3a6969%2fannounce&tr=udp%3a%2f%2fopen.demonii.com%3a1337&tr=udp%3a%2f%2fp4p.arenabg.ch%3a1337%2fannounce&tr=udp%3a%2f%2ftorrent.gresille.org%3a80%2fannounce&tr=udp%3a%2f%2ftracker.aletorrenty.pl%3a2710%2fannounce&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.glotorrents.com%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.internetwarriors.net%3a1337&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fzer0day.ch%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.pirateparty.gr%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2ftracker.open-internet.nl%3a6969%2fannounce&tr=%20udp%3a%2f%2fmgtracker.org%3a6969%2fannounce')

    topTable = False
    canGetHref = False
    inHREFCELL = False
    canGetSize = False
    canGetSeed = False
    canGetLeech = False
    current_record = dict()
    current_record.clear()

    def handle_starttag (self,tag,attrs):
        myTag = tag
        params = dict(attrs)

        if myTag == self.TD and (params.get('class') == 'v' or params.get('class') == 'n'):
            self.inHREFCELL = True
        if myTag == self.A and params.get('href') and self.inHREFCELL:
            working_url = params.get('href')
            if re.match(r'\/torrent', working_url):
                self.current_record['desc_link'] = URL + params.get('href')
                
                # print(self.current_record['desc_link'])
                self.inHREFCELL = False
                #Get Name
                second_page = retrieve_url(self.current_record['desc_link'])
                self.current_record['name'] = re.findall(self.GET_NAME_RE, second_page)[0].replace('|','')
                #Get Hash -- will use these to make the magnet link
                thisHash = re.findall(self.GET_HASH_RE, second_page)[0]
                self.current_record['link'] = 'magnet:?xt=urn:btih:' + thisHash + '&dn=' + self.current_record['name'] + self.TRACKERS

            else:
                pass
        
        if myTag == self.TD and params.get('class') == 's':
            self.canGetSize = True
        if myTag == self.TD and params.get('class') == 'u':
            self.canGetSeed = True
        if myTag == self.TD and params.get('class') == 'd':
            self.canGetLeech = True

    def handle_data(self, data):
        
        if self.canGetSize:
            self.current_record['size'] = data  
            self.canGetSize = False
        if self.canGetSeed:
            self.current_record['seeds'] = data
            self.canGetSeed = False
        if self.canGetLeech:
            self.current_record['leech'] = data
            self.canGetLeech = False
            self.current_record['engine_url'] = URL

    def handle_endtag(self,tag):
        myTag = tag
        # We are now at the end of the row. Time to save current row.
        if myTag == self.TR:
            if len(self.current_record) == 7:
                the_results.append(dict(self.current_record))
                self.current_record.clear()
            else:
                self.current_record.clear()

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

    def __init__(self):
        pass

    def search(self, what, cat='all'):
        query = str(what).replace(r' ', '+')
        page = 1
        total_records = 0
        curr_record = 0
        a = yourBitParser()
        while (int(total_records) >= curr_record ):
            full_url = self.url + '/?q=' + query + '&c=' + self.supported_categories[cat.lower()] + '&page=' + str(page)
            b = retrieve_url(full_url)
            # print(full_url)
            try:
                total_records = re.findall(a.GET_NUM_RESULTS, b)[0]
            except IndexError:
                quit()

            a.feed(b)
            for each_record in the_results:
                curr_record += 1
                # print(total_records)
                # print(curr_record)
                prettyPrinter(each_record)
                pass
            page += 1
            the_results.clear()
            pass


if __name__ == '__main__':
    a = yourbittorrent()
    a.search('acre','all')
