import sys

from service.scraper import Scraper

print('Scraping all the centers for Region {}...'.format(sys.argv[1]))
Scraper.scrape_and_write(sys.argv[1])
