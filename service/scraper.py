import scrapers.mittvaccin as mittvaccin


class Scraper(object):
    @staticmethod
    def scrape(centers):
        next_available_times = []

        for center in centers:
            if 'https://bokning.mittvaccin.se/' in center['link']:

                id = int(mittvaccin.get_id_from_url(center['link']))

                next_available_time = mittvaccin.get_next_available_time(
                    id, '210517', '210630')
                next_available_time = {
                    'center': center['vaccination_center'],
                    'link': center['link'],
                    'next': next_available_time['next'],
                    'amount_of_slots': next_available_time['amount_of_slots']
                }

                next_available_times.append(dict(next_available_time))

        return next_available_times
