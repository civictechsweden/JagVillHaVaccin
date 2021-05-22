from service.scraper import Scraper

print('Scraping all the centers for Region Jönköping...')
Scraper.scrape_and_write('jonkoping')
