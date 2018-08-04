#VERSION: 0.4
#AUTHORS: nindogo

import re
from html.parser import HTMLParser

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
URL = 'https://yourbittorrent.com'


class yourBitParser(HTMLParser):
    A, TD, TR, HREF, TABLE, DIV, INPUT, BODY = (
         'a', 'td', 'tr', 'href', 'table', 'div', 'input', 'body')
    GET_NUM_RESULTS = re.compile(r'<\/b> of <b>(\d*)<\/b> torrents found for "')
    GET_NAME_RE = re.compile(r'<!DOCTYPE html><html lang="en-US"><head><title>(.*)Torrent Download</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1')
    GET_HASH_RE = re.compile(r'<\/td><\/tr><tr><td><b>Hash<\/td><td>(.*)<\/td><\/tr><tr><td valign=top><b>Rating<\/td><td id="')

    the_results = []

    topTable = False
    canGetHref = False
    inHREFCELL = False
    canGetSize = False
    canGetSeed = False
    canGetLeech = False
    canGetName = False
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
                self.canGetName = True
                self.current_record['link'] = URL + r'/down/' + self.current_record['desc_link'].split(r'/')[4] + '.torrent'
                
                # Prepare to Get Name
                self.current_record['name'] = str()
                

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
        if self.inHREFCELL and self.canGetName:
            if self.current_record['name']:
                self.current_record['name'] = self.current_record['name'] + data
            else:
                self.current_record['name'] = data

    def handle_endtag(self,tag):
        myTag = tag
        # We are now at the end of the row. Time to save current row.
        if myTag == self.TR:
            if len(self.current_record) == 7:
                # self.the_results.append(dict(self.current_record))
                prettyPrinter(self.current_record)
                self.current_record.clear()
            else:
                self.current_record.clear()
        if myTag == self.A and self.canGetName == True and self.inHREFCELL == True:
                    self.canGetName = False
                    self.inHREFCELL = False

            

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
        a = yourBitParser()
        while True:

            full_url = self.url + '/?q=' + query + '&c=' + self.supported_categories[cat.lower()] + '&page=' + str(page)
            b = retrieve_url(full_url)
            # print(full_url)
            try:
                total_records = a.GET_NUM_RESULTS.findall(b)[0]
            except IndexError:
                quit()

            a.feed(b)
            page += 1


if __name__ == '__main__':
    a = yourbittorrent()
    a.search('bbc','all')
