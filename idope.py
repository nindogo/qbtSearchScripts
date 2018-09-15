#VERSION 0.92
#AUTHOR nindogo

import logging

import re
from html.parser import HTMLParser
from helpers import retrieve_url
from novaprinter import prettyPrinter

logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)


class iDopeHTMLParser(HTMLParser):
    A, TD, TR, HREF, TABLE, DIV, INPUT, BODY, HTML = (
        'a', 'td', 'tr', 'href', 'table', 'div', 'input', 'body', 'html')
    tracker_list = '&tr=http%3A%2F%2Fopen.trackerlist.xyz%3A80%2Fannounce&tr=udp%3A%2F%2Ft.opentracker.xyz%3A80%2Fannounce&tr=udp%3A%2F%2Fipv4.opentracker.xyz%3A80%2Fannounce&tr=udp%3A%2F%2Fbt.xxx-tracker.com%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=http%3A%2F%2Ft.nyaatracker.com%3A80%2Fannounce&tr=udp%3A%2F%2Fbigfoot1942.sektori.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.port443.xyz%3A6969%2Fannounce&tr=https%3A%2F%2Fopentracker.xyz%3A443%2Fannounce&tr=udp%3A%2F%2Ftracker.vanitycore.co%3A6969%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=http%3A%2F%2Ftorrent.nwps.ws%3A80%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.si%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.tfile.me%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=http%3A%2F%2Ftherightsize.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv6.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Fthetracker.org%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.justseed.it%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker4.itzmx.com%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.com%3A2710%2Fannounce&tr=udp%3A%2F%2Fretracker.hotplug.ru%3A2710%2Fannounce&tr=http%3A%2F%2Fshare.camoe.cn%3A8080%2Fannounce&tr=udp%3A%2F%2Fpublic.popcorn-tracker.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.iamhansen.xyz%3A2000%2Fannounce&tr=http%3A%2F%2Fretracker.telecom.by%3A80%2Fannounce&tr=http%3A%2F%2Ftracker.corpscorp.online%3A80%2Fannounce&tr=https%3A%2F%2F2.track.ga%3A443%2Fannounce&tr=http%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Fipv6.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=http%3A%2F%2F0d.kebhana.mx%3A443%2Fannounce&tr=http%3A%2F%2Ftracker.city9x.com%3A2710%2Fannounce&tr=http%3A%2F%2Fretracker.mgts.by%3A80%2Fannounce&tr=https%3A%2F%2Fopen.trackerlist.org%3A443%2Fannounce&tr=https%3A%2F%2Ftracker.trackerlist.org%3A443%2Fannounce&tr=https%3A%2F%2Ftracker.fastdownload.xyz%3A443%2Fannounce&tr=udp%3A%2F%2Ftracker.swateam.org.uk%3A2710%2Fannounce&tr=udp%3A%2F%2Fdenis.stalker.upeer.me%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.msm8916.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fzephir.monocul.us%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker1.itzmx.com%3A8080%2Fannounce&tr=udp%3A%2F%2Fmgtracker.org%3A6969%2Fannounce&tr=https%3A%2F%2Fcernet-tracker.appspot.com%3A443%2Fannounce&tr=http%3A%2F%2Ftracker.veryamt.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.dler.org%3A6969%2Fannounce&tr=http%3A%2F%2Fomg.wtftrackr.pw%3A1337%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker2.itzmx.com%3A6961%2Fannounce'
    curr_result = dict()
    curr_page = list()
    in_record_row = False
    can_get_name = False
    can_get_length = False
    can_get_hash = False
    url = 'https://idope.top'

    # SCAN_RESULT_PAGE = re.compile('<div class="resultdivtopname">(.+?)<\/div>.*?<div class="resultdivbottonlength">(.+?)<\/div>.*?<div class="resultdivbottonseed">(.+?)<\/div>.*?')

    def handle_starttag(self, tag, attrs):
        myTag = tag
        params = dict(attrs)

        if myTag == self.DIV and params.get('class') == 'resultdiv':
            self.in_record_row = True
            self.can_get_hash = False
            self.can_get_length = False
            self.can_get_name = False

        elif self.in_record_row and myTag == self.DIV and params.get('class') == 'resultdivtopname':
            self.can_get_name = True

        elif self.in_record_row and myTag == self.DIV and params.get('class') == 'resultdivbottonlength':
            self.can_get_length = True

        elif self.in_record_row and myTag == self.DIV and params.get('class') == 'resultdivbottonseed':
            self.can_get_hash = True

        elif self.in_record_row and myTag == self.DIV and params.get('class') == 'magneticdiv':
            self.in_record_row = False

    def handle_data(self, data):
        if self.can_get_name is True:
            self.curr_result['name'] = str(data).strip()
            self.can_get_name = False

        if self.can_get_length is True:
            if data == 'N/A':
                self.curr_result['size'] = -1
            else:
                self.curr_result['size'] = str(data).replace(',', '')
            self.can_get_length = False

        if self.can_get_hash is True:
            self.curr_result['link'] = str('magnet:?xt=urn:btih:' +
                                           data +
                                           '&dn=' +
                                           self.curr_result['name'] +
                                           self.tracker_list
                                           )
            self.can_get_hash = False
            self.curr_result['seeds'] = -1
            self.curr_result['leech'] = -1
            self.curr_result['desc_link'] = str(-1)
            self.curr_result['engine_url'] = self.url
            # prettyPrinter(self.curr_result)
            # print(type(self.curr_result['size']))
            self.curr_page.append(dict(self.curr_result))
            self.curr_result.clear()

    def handle_endtag(self, tag):
            myTag = tag
            if myTag == self.BODY:
                if len(self.curr_page) == 0:
                    quit()

                for each_record in self.curr_page:
                    prettyPrinter(each_record)

                self.curr_page.clear()


class idope(object):
    logging.debug('Started the iDope class')
    url = 'https://idope.top'
    name = 'iDope'
    supported_categories = {
        'all': ''}
        
    def search(self, what='ncis', cat='all'):
        logging.debug('Searching now')
        query = what

        for i in range(1, 1000, 1):
            search_url = 'https://idope.top/s/' + query + '/page/' + str(i)
            a = retrieve_url(search_url)
            b = iDopeHTMLParser()
            b.feed(a)
            pass


if __name__ == '__main__':
    logging.debug('Running from file.')
    a = idope()
    a.search('csi')
