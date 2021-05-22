import json
import urllib.request


class Downloader(object):
    @staticmethod
    def get(url):
        try:
            return urllib.request.urlopen(url).read()
        except urllib.error.HTTPError as err:
            print(f'ERROR {err.code}: Could not download {url}.')

    @staticmethod
    def get_json(url):
        return json.loads(Downloader.get(url).decode('utf-8'))
