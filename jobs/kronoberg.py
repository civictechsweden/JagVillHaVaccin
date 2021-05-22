from service.scraper import Scraper

print('Scraping all the centers for Region Kronoberg...')
Scraper.scrape_and_write('kronoberg')
