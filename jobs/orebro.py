from service.scraper import Scraper

print('Scraping all the centers for Region Örebro...')
Scraper.scrape_and_write('orebro')
