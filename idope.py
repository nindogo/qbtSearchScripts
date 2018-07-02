# Version 0.5
# Author nindogo

import logging

# logging.basicConfig(level=logging.INFO)
# logging.getLogger(__name__)

try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser
# qBt
from novaprinter import prettyPrinter
from helpers import retrieve_url 
# others
import re

BASES = 1024
SIZES = {"KB": BASES, "MB": BASES**2, "GB": BASES**3}
URL = 'https://idope.se/torrent-list/'
URL0 = 'https://idope.se/'
globalResults = []
globalResults.clear()



class idopeHTMLParser(HTMLParser):
    logging.debug('parser initiated')
    #Variables will be added here
    A, TD, TR, HREF, TABLE, DIV, INPUT = (
         'a', 'td', 'tr', 'href', 'table', 'div', 'input')
    current_row = {}
    current_page = []
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
    URL = 'https://idope.se'

    # def __init__(self, res=[]):
    #     try:
    #         super().__init__()
    #     except:
    #         HTMLParser.__init__(self)
    #     current_page = res

    #These two are already known
    current_row['leech'] = -1
    current_row['engine_url'] = URL0

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
            self.desc_link = ('https://idope.se' + params.get('href'))
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
            # self.current_page.append(self.current_row)
            globalResults.append(dict(self.current_row))
            self.inRecordRow = False
            # self.current_row.clear()
            # logging.debug('Current row is now {}'.format(self.current_row))
            # print('The length of results is now: ', len(globalResults))

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
            self.current_row['name'] = data
            logging.debug(data)
            self.canGetName = False
            self.current_row['link'] = 'magnet:?xt=urn:btih:' + self.desc_link.split('/')[5] + '&dn=' + data + self.magnet_trackers


    def handle_comment(self,data):
        if self.inHidepage:
            pn =(re.findall(r'\d+', data))
            for q in pn:
                # print(q)
                self.totalPages = q
            # print(re.fullmatch(r'\d+',data))
            self.inHidepage = False


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
    url = 'https://idope.se/'
    current = {}
    idope_parser = idopeHTMLParser()

    def search(self, what='ncis', cat='all'):
        logging.debug('Searching now')
        query = what
        curr_page = 1
        
        while ((curr_page < 101) and (curr_page <= int(self.pages))):
            full_url = URL + query + '?p=' +  str(curr_page) + '&c=' + self.supported_categories[cat.lower()]
            # logging.debug(full_url)
            # print(full_url)
            page_htm = retrieve_url(full_url)
            self.idope_parser.feed(page_htm)
            self.pages = self.idope_parser.totalPages
            curr_page += 1
            for current in globalResults:
                # current = current_page
                # print(current.get('name'))
                prettyPrinter(current)
            globalResults.clear()
        self.idope_parser.close()


if __name__ == '__main__':
    idopeObject = idope
    idope.search(idope, 'Acre', 'aniMe')
    logging.debug('And now we are done')
