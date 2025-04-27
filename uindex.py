#VERSION: 0.1
# AUTHORS: nindogo
# LICENSING INFORMATION

import re
from datetime import timedelta, datetime
from html.parser import HTMLParser
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
# some other imports if necessary

def de_pub_date(date_string):
	this_date = date_string.split()
	if len(this_date) == 3:
		t1 = timedelta()
		if this_date[1] == "minutes":
			t1 = timedelta(minutes=float(this_date[0]))
		if this_date[1] == "hours":
			t1 = timedelta(hours=float(this_date[0]))
		if this_date[1] == "days":
			t1 = timedelta(days=float(this_date[0]))
		if this_date[1] == "weeks":
			t1 = timedelta(weeks=float(this_date[0]))
		if this_date[1] == "months":
			this_date[1] = "weeks"
			this_date[0] = str(30 * float(this_date[0]))
			return de_pub_date(' '.join(this_date))
		if this_date[1] == "years":
			this_date[1] = "days"
			this_date[0] = str(365 * float(this_date[0]))
			return de_pub_date(' '.join(this_date))
		
		return int((datetime.now() - t1).timestamp())

class uindex(object):
    """
    `url`, `name`, `supported_categories` should be static variables of the engine_name class,
     otherwise qbt won't install the plugin.

    `url`: The URL of the search engine.
    `name`: The name of the search engine, spaces and special characters are allowed here.
    `supported_categories`: What categories are supported by the search engine and their corresponding id,
    possible categories are ('all', 'anime', 'books', 'games', 'movies', 'music', 'pictures', 'software', 'tv').
    """

    url = 'https://uindex.org'
    name = 'UIndex'
    supported_categories = {
        'all': '',
        'anime': '&c=7',
        'games': '&c=3',
        'movies': '&c=1',
        'music': '&c=4',
        'software': '&c=5',
        'tv': '&c=2'
    }

    def __init__(self):
        """
        Some initialization
        """

    def download_torrent(self, info):
        """
        Providing this function is optional.
        It can however be interesting to provide your own torrent download
        implementation in case the search engine in question does not allow
        traditional downloads (for example, cookie-based download).
        """
        print(download_file(info))

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        """
        Here you can do what you want to get the result from the search engine website.
        Everytime you parse a result line, store it in a dictionary
        and call the prettyPrint(your_dict) function.

        `what` is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
        `cat` is the name of a search category in ('all', 'anime', 'books', 'games', 'movies', 'music', 'pictures', 'software', 'tv')
        """
        
        find_string = r"""<tr>.*?<a href=["'](?P<link>magnet.*?)["'].*?""" \
                    + r"""<a href=["'](?P<desc_link>[^"']*?)["']""" \
                    + r""">(?P<name>[^<]*?)<.*?""" \
                    + r"""class=["']sub["'][^>]*>(?P<pub_date>[^<]*)<.*?""" \
                    + r"""style=['"]white-space:nowrap[^>]*?>(?P<size>[^<]*?)<.*?""" \
                    + r"""class="g".*?>(?P<seeds>[^<]*?)<.*?""" \
                    + r"""class="b"*?>(?P<leech>[^<]*?)<.*?"""
        
        find_torrent = re.compile(find_string, flags=(re.M|re.S))
        
        query = self.url + "/search.php?search=" + what.replace("%20", "+") + \
				self.supported_categories[cat] + '&sort=seeders&order=DESC'
        page = retrieve_url(query)
        matches = re.finditer(find_torrent, page)
        for match in matches:
            result_dict = {}
            result_dict = match.groupdict()
            result_dict["desc_link"] = self.url + result_dict["desc_link"] 
            result_dict["size"] = result_dict["size"].rstrip()
            result_dict["pub_date"] = result_dict["pub_date"].rstrip()
            result_dict["pub_date"] = de_pub_date(result_dict['pub_date'])
            result_dict["engine_url"] = self.url
            prettyPrinter(result_dict)


if __name__ == "__main__":
    engine = uindex()
    engine.search('Law')
