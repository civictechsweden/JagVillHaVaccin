import json

import scrapers.mittvaccin as mittvaccin
import scrapers.vaccina as vaccina
import scrapers.elva77 as elva77

from service.writer import Writer


class Scraper(object):
    def scrape_centers_from_1177(already_fetched_urls):
        centers = elva77.get_vaccination_centers()

        centers_json = []

        for center in centers:
            url = elva77.BASE_URL + center['Url']

            if url not in already_fetched_urls:
                centers_json.append(dict(elva77.get_center_info(
                    center['Url'])))
            else:
                print('Not fetching this one: {}'.format(url))

        return centers_json

    def scrape_centers_from_manual_lists():

        regions = [
            'blekinge', 'jonkoping', 'kalmar', 'kronoberg', 'orebro', 'skane',
            'sodermanland', 'vasterbotten', 'vastragotaland'
        ]

        centers_json = []

        for region in regions:
            with open('centers/' + region + '.json') as json_file:
                region_centers = json.load(json_file)

                for center in region_centers:
                    if 'address' in center and center['address'] != '':
                        centers_json.append(
                            elva77.create_unlisted_center(center))
                    else:
                        url = elva77.search_center(
                            center['vaccination_center'] + ' ' +
                            center['municipality'])

                        if url:
                            center_info = dict(elva77.get_center_info(url))
                            if center['link'] != '':
                                center_info['platform_url'] = center['link']
                                platform = elva77.get_platform(center['link'])
                                center_info['platform'] = platform

                                if platform == 'MittVaccin':
                                    center_info[
                                        'platform_id'] = mittvaccin.get_id_from_url(
                                            center['link'])
                                center_info[
                                    'appointment_by_phone_only'] = not elva77.is_fetchable(
                                        platform)

                            if 'category' in center and center[
                                    'category'] != '':
                                center_info['name'] = '{} ({})'.format(
                                    center_info['name'], center['category'])

                            if 'id' in center and center['id'] != '':
                                center_info['platform_id'] = center['id']

                            centers_json.append(center_info)
                        else:
                            print("Couldn't find {} on 1177".format(
                                center['vaccination_center']))

        return centers_json

    def scrape_times(centers):
        next_available_times = []

        for center in centers:
            if 'https://bokning.mittvaccin.se/' in center['link']:

                id = int(mittvaccin.get_id_from_url(center['link']))

                next_available_time = mittvaccin.get_next_time_and_slots(
                    id, '210517', '210630')
                next_available_time = {
                    'center': center['vaccination_center'],
                    'link': center['link'],
                    'next': str(next_available_time['next']),
                    'amount_of_slots': next_available_time['amount_of_slots']
                }

                next_available_times.append(dict(next_available_time))

        return next_available_times

    def scrape_and_write_centers():
        centers_from_manual_lists = Scraper.scrape_centers_from_manual_lists()

        already_fetched_urls = [
            center['1177_url'] for center in centers_from_manual_lists
            if '1177_url' in center
        ]

        centers_from_1177 = Scraper.scrape_centers_from_1177(
            already_fetched_urls)

        centers = sorted(centers_from_1177 + centers_from_manual_lists,
                         key=lambda k: k['name'])
        Writer.write_json(centers, 'centers.json')

    def scrape_and_write_times(region):
        with open('centers/' + region + '.json') as json_file:
            centers_blekinge = json.load(json_file)

        next_available_times = Scraper.scrape_times(centers_blekinge)

        Writer.write_csv(next_available_times, region + '.csv')
