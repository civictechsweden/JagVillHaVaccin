import json

from service.scraper import Scraper
from service.writer import Writer


def scrape_and_write(region):
    with open('centers/' + region + '.json') as json_file:
        centers_blekinge = json.load(json_file)

    next_available_times = Scraper.scrape(centers_blekinge)

    Writer.write(next_available_times, region + '.csv')


print('Scraping all the centers for Region Blekinge...')
#scrape_and_write('blekinge')

print('Scraping all the centers for Region Jönköping...')
#scrape_and_write('jonkoping')

print('Scraping all the centers for Region Kalmar...')
#scrape_and_write('kalmar')

print('Scraping all the centers for Region Kronoberg...')
#scrape_and_write('kronoberg')

print('Scraping all the centers for Region Örebro...')
scrape_and_write('orebro')
