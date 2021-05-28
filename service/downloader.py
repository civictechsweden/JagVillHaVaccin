import html
import time
import json
import urllib.request

from bs4 import BeautifulSoup


class Downloader(object):
    @staticmethod
    def get(url):
        try:
            return urllib.request.urlopen(url).read()
        except urllib.error.HTTPError as err:
            print(f'ERROR {err.code}: Could not download {url}.')
            if (err.code == 429):
                print('Retrying in 3 seconds')
                time.sleep(3)
                return Downloader.get(url)
            else:
                print('Permanent error: skipping this center')
                return None

    @staticmethod
    def get_json(url):
        return json.loads(Downloader.get(url).decode('utf-8'))

    @staticmethod
    def get_html_soup(url):
        response = Downloader.get(url)
        htmlData = html.unescape(response.decode('utf-8'))
        return BeautifulSoup(htmlData, 'html.parser')
