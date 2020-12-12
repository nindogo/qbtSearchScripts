#VERSION 20201212
#Author nindogo
import json

import threading

from novaprinter import prettyPrinter
from helpers import retrieve_url

class solidtorrents(object):
    url = "https://solidtorrents.net"
    name = 'Solid Torrents'
    supported_categories = {'all': 'all'}

    def __init__(self):
        pass

    def process_record(self, record):
        this_record = dict()
        this_record['name'] = record['title']
        this_record['link'] = record['magnet']
        this_record['size'] = str(record['size']) + ' B'
        this_record['engine_url'] = self.url
        this_record['seeds'] = record['swarm']['seeders']
        this_record['leech'] = record['swarm']['leechers']
        this_record['desc_link'] = self.url + '/view/' + record['_id']
        prettyPrinter(this_record)

    def launch_request(self, query, skip):
        this_query = query + '&fuv=yes&skip=' + str(skip)
        these_items = json.loads(retrieve_url(this_query))
        for item in these_items['results']:
            self.process_record(item)

    def search(self, what, cat='all'):

        query = self.url + '/api/v1/search/?q='\
                + what\
                + '&sort=seeders&category='\
                + self.supported_categories[cat]

        response = json.loads(retrieve_url(query))
        all_results = response['hits']['value']
        for item in response['results']:
            self.process_record(item)

        i = 20
        threads = list()
        while all_results > i :
            a = threading.Thread(target=self.launch_request,
                                 args=(query, i)
                                 )

            threads.append(a)
            a.start()
            i += 20

        for thread in threads:
            thread.join()
