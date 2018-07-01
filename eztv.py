#VERSION: 0.2
#AUTHORS: nindogo

import re
import logging
import copy

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser
# qBt
from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
#others
import re

URL = "https://eztv.ag"
globalResponse=[]



class eztvHtmlParser(HTMLParser):
        A, TD, TR, HREF, TABLE, SCRIPT= ('a', 'td', 'tr', 'href', 'table', 'script')
        inTableRow = False
        inTable = False
        current_item = {}
        url = URL
        # responseCount
        # response= []
    
        # can not get these.
        current_item['leech'] = -1
        current_item['engine_url'] =URL

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            myTag = tag
            
            if (params.get('class') == 'forum_header_border' and params.get('name') == 'hover'):
                self.inTableRow = True
                self.inTable = True

            if myTag == self.A and self.inTableRow and params.get('class') == 'magnet':
                self.current_item['link'] = params.get('href')
                
            if myTag == self.A and self.inTableRow and params.get('class') == 'epinfo':
                self.current_item['desc_link'] = self.url + params.get('href')
                a = re.compile(r' \[').split(params.get('title'))[0]
                self.current_item['name'] = a
                # logging.debug("Params: %s" % params)
            
            if myTag == self.TD and params.get('class') == 'forum_thread_post_end' and params.get('align') == 'center':
                globalResponse.append(dict(self.current_item))
                self.inTable = False
                self.inTableRow = False
                

        def handle_data(self, data):
            if self.inTableRow and (data.endswith('MB') or data.endswith('GB') or data.endswith('KB')):
                self.current_item['size'] = data
                print(data)
            #     pass

            if self.inTableRow and (data.isalnum() or (data == '-')):
                if data.isalnum():
                    self.current_item['seeds'] = int(data)
                elif data == '-':
                    self.current_item['seeds'] = 0

            # if self.inTableRow and (data.endswith('[eztv]')):
            #     self.current_item['name'] = data

        def handle_endtag(self, tag):
            myTag = tag
            if self.inTableRow and myTag == self.TR:
                self.inTableRow = False
                # prettyPrinter(self.current_item)
                # print(len(self.current_item))'

            if myTag == self.TABLE:
                self.inTable = False
            
            if self.inTable:
                # response.append(self.current_item)
                print(len(globalResponse))
            elif not self.inTable:
                # print('this is response',response)
                # logging.debug('ending')
                # return response
                pass



class eztv(object):
    logging.debug("Class Initiated")
    name = "EZTV"
    supported_categories = {'tv': 'tv', 'all': 'all'}
    url = 'https://eztv.ag/'

    def search(self,what,cat='all'):
        logging.debug("Searching")
        query = what.replace('%20','-')
        query = ('https://eztv.ag/search/' + query)
        eztvParser = eztvHtmlParser()
        eztvHtml = retrieve_url(query)
        eztvParser.feed(eztvHtml)
        for k in globalResponse:
            prettyPrinter(k)
        eztvParser.close()


if __name__ == '__main__':
    z = eztv()
    z.search('Acre', 'all')
