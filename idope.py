#VERSION: 0.91
#AUTHORS: nindogo

import threading
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)

import re
from html.parser import HTMLParser
from helpers import retrieve_url
from novaprinter import prettyPrinter


class idopeHTMLParser(threading.Thread, HTMLParser):
    page_link = threading.local()
    A, TD, TR, HREF, TABLE, DIV, INPUT, BODY = (
        'a', 'td', 'tr', 'href', 'table', 'div', 'input', 'body')
    logging.debug('parser initiated')
    
    current_row = {}
    magnet_trackers = str()
    totalPages = int()
    desc_link = str()
    inRecordRow = False
    theTopRecords = False
    theBottonRecords = False
    canGetSize = False
    canGetSeeds = False
    canGetName =False
    inHidepage = False
    URL = 'https://idope.cc'
    def __init__(self, url):
        self.page_link = url
        HTMLParser.__init__(self)
        threading.Thread.__init__(self)

    def run(self):
        # print(self.page_link)
        self.feed(retrieve_url(self.page_link))

    

    #These two are already known
    current_row['leech'] = -1
    current_row['engine_url'] = URL

    def handle_starttag(self,tag,attrs):
        myTag = tag
        params = dict(attrs)
        
        #get Torrent Trackers
        if myTag == 'input' and params.get('id') == 'hidetrack' and params.get('style') == 'display:none':
            self.magnet_trackers = params.get('value')
            logging.debug('The trackers have been entred {}'.format(self.magnet_trackers))
        
        #Reading a row of responses starts below.
        elif myTag == self.DIV and params.get('class') == 'resultdiv':
            self.inRecordRow = True
            logging.debug('Entered a row now')

        elif myTag == self.DIV and self.inRecordRow and params.get('class') == 'resultdivtop':
            self.theTopRecords = True
        
        #getting desc_link
        elif myTag == self.A and self.theTopRecords and self.inRecordRow:
            self.desc_link = ('https://idope.cc' + params.get('href'))
            self.current_row['desc_link'] = self.desc_link
            logging.debug('desc_link :{}'.format(self.desc_link))
            # print('the description link is',self.desc_link)

        #Got both the disc_url and some input for link now move on to the bottom.
        elif myTag == self.DIV and self.theTopRecords and self.inRecordRow and params.get('class') == 'resultdivbotton':
            self.theTopRecords = False
            self.theBottonRecords = True

        #get the size
        elif myTag == self.DIV and self.theBottonRecords and self.inRecordRow and params.get('class') == 'resultdivbottonlength':
            self.canGetSize = True
        
        #get the seeds
        elif  myTag == self.DIV and self.theBottonRecords and self.inRecordRow and params.get('class') == 'resultdivbottonseed':
            self.canGetSeeds = True
        
        #get the name
        elif myTag == self.DIV and self.theBottonRecords and self.inRecordRow and params.get('class') == 'hideinfohash' and 'hidename' in params.get('id'):
            self.canGetName =True

        elif myTag == self.DIV and params.get('class') == 'magneticdiv' and self.inRecordRow and self.current_row :
            prettyPrinter(self.current_row)
            self.inRecordRow = False
            logging.debug('Current row is now {}'.format(self.current_row))

        elif myTag == self.DIV and params.get('id') == 'hidepage':
            self.inHidepage = True


    def handle_data(self, data):
        if self.canGetSize and self.theBottonRecords and self.inRecordRow:
            logging.debug(data)
            self.current_row['size'] = data
            logging.debug('the size is: {}'.format(data))
            self.canGetSize = False

        if self.canGetSeeds and self.theBottonRecords and self.inRecordRow:
            self.current_row['seeds'] = data
            self.canGetSeeds = False
        
        #Now that we have the name - we can get the link
        if self.theBottonRecords and self.inRecordRow and self.canGetName:
            self.current_row['link'] = 'magnet:?xt=urn:btih:' + self.desc_link.split('/')[5] + '&dn=' + self.current_row['name'] + self.magnet_trackers


    def handle_comment(self,data):
        if self.inHidepage:
            pn =(re.findall(r'\d+', data))
            for q in pn:
                # print(q)
                self.totalPages = q
            # print(re.fullmatch(r'\d+',data))
            self.inHidepage = False

        if self.theTopRecords and self.inRecordRow:
            pn = (re.findall(r'">(.*)<\/', data))
            self.current_row['name'] = str(pn)[2:-3].replace(r'|', '')
            
    def handle_endtag(self, tag):
        myTag = tag
        if myTag == self.BODY:
            quit()


class idope(object):
    logging.debug('Class Initiated')
    supported_categories= {
        'all':''
        ,'video':'2'
        ,'movies':'1'
        ,'tv':'3'
        ,'games':'7'
        ,'music':'6'
        ,'anime':'4'
        ,'software':'8'
        ,'books':'9'
        ,'xxx':'5'
        ,'others':'0'
        }
    pages = 1
    name = 'iDope'
    url = 'https://idope.cc/'
    current = {}
    SEE_TOTAL_PAGES = re.compile(r'<!--<div\s+id="hidemaxpage">(\d+)<\/div>-->')

    def search(self, what='ncis', cat='all'):
        logging.debug('Searching now')
        query = what
        curr_page = 1
        first_page_url = 'https://idope.cc/torrent-list/' + query + '?p=' + str(curr_page) + '&c=' + self.supported_categories[cat.lower()]
        first_page_htm = retrieve_url(first_page_url)
        self.pages = self.SEE_TOTAL_PAGES.findall(first_page_htm)[0]

        while ((curr_page < 101) and (curr_page <= int(self.pages)) and (self.pages != 0)):
            full_url = 'https://idope.cc/torrent-list/' + query + '?p=' +  str(curr_page) + '&c=' + self.supported_categories[cat.lower()]
            logging.debug(full_url)
            idope_parser = idopeHTMLParser(full_url)

            idope_parser.start()
            curr_page += 1


if __name__ == '__main__':
    idopeObject = idope
    idope.search(idope, 'minute', 'all')
    logging.debug('And now we are done')
