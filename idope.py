#VERSION: 0.93
#AUTHORS: nindogo

import logging

import re
import threading
from helpers import retrieve_url
from novaprinter import prettyPrinter


logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

def search_threaded(url):
    logging.debug('Starting a new thread.')
    # PAGE_QUERY = re.compile(r'<a href="(magnet.*?)">.*?<span style="padding:0 5px 10px 7px;word-wrap: break-word;">(.+?)<\/span>.*?<span>Seed:(.*?)<\/span>.*?<\/i>(.*?)<\/span>', re.DOTALL)
    page_query_regex = re.compile('break-word;">(.*?)</span>.*?Seed:(.*?)</span>.*?Leech:(.*?)</span>.*?Size:(.*?)</span>.*?href="(magnet.*?)"', re.DOTALL)
    magnet_query_regex = re.compile('href="(magnet.*?)"')
    empty_page_regex = re.compile(r'(<h3 style="color:blue;">No Results Found for \()')
    curr_record = list()
    curr_dict = dict()
    curr_record.clear()
    curr_dict.clear()
    try:
        a_v = retrieve_url(url)
    except:
        print('failed to connect')
        quit()
    match = re.search(empty_page_regex, a_v)
    if match:
        print('another one bites the dust')
        quit()
    c_v = re.findall(magnet_query_regex, a_v)
    for b_v in re.finditer(page_query_regex, a_v):
        for x in range(1, 5, 1):
            curr_record.append(b_v.group(x).strip())
        curr_dict['link'] = c_v[x]
        curr_dict['name'] = curr_record[0]
        curr_dict['seeds'] = curr_record[1]
        curr_dict['size'] = curr_record[3].replace(',', '')
        curr_dict['leech'] = curr_record[2]
        curr_dict['engine_url'] = 'https://www.idope.site'
        curr_dict['desc_link'] = str(-1)
        curr_record.clear()
        prettyPrinter(curr_dict)
        curr_dict.clear()


class idope(object):
    logging.debug('Started the iDope class')
    url = 'https://www.idope.site'
    name = 'iDope'
    supported_categories = {
        'all': ''}

    PAGE_QUERY = re.compile(r'<a href="(magnet.*?)">.*?<span style="padding:0 5px 10px 7px;word-wrap: break-word;">(.+?)<\/span>.*?<span>Seed:(.*?)<\/span>.*?<\/i>(.*?)<\/span>', re.DOTALL)
    EMPTY_PAGE_QUERY = re.compile(r'(<h3 style="color:blue;">No Results Found for \()')
    curr_record = list()
    curr_dict = dict()

    def search(self, what='ncis', cat='all'):
        logging.debug('Searching now')
        query = what

        logging.debug('Starting the testing')
        for i in range(1, 1000, 1):
            search_url = 'https://www.idope.site/s/' + query + '/page/' +str(i)
            t = threading.Thread(target=search_threaded, args=(search_url,))
            t.start()


if __name__ == '__main__':
    logging.debug('Running from file.')
    a = idope()
    a.search('ncis')
