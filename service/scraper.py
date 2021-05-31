import json
import string
from os import replace

import scrapers.mittvaccin as mittvaccin
import scrapers.elva77 as elva77
import scrapers.vgr as vgr

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

    def scrape_centers_from_vgr(already_fetched_urls):
        centers = vgr.get_centers()

        centers_json = []

        for center in centers:
            url = center['urlContactCard']

            if 'https://www.1177.se' in url:
                short_url = url.replace(elva77.BASE_URL + '/Vastra-Gotaland',
                                        '')

                print('1177:    ' + short_url)

                if url not in already_fetched_urls:
                    center_json = elva77.get_center_info(short_url)

                else:
                    print('Not fetching this one: {}'.format(url))

            else:
                print('Not 1177:    ' + url)
                center_json = elva77.create_unlisted_center(
                    vgr.convert_center(center))

            center_json['appointment_by_phone_only'] = False
            centers_json.append(dict(center_json))

        return centers_json

    def scrape_and_write_centers():
        centers_from_manual_lists = Scraper.scrape_centers_from_manual_lists()

        already_fetched_urls = [
            center['1177_url'] for center in centers_from_manual_lists
            if '1177_url' in center
        ]

        centers_from_vgr = Scraper.scrape_centers_from_vgr(
            already_fetched_urls)

        already_fetched_urls = already_fetched_urls + [
            center['1177_url']
            for center in centers_from_vgr if '1177_url' in center
        ]

        centers_from_1177 = Scraper.scrape_centers_from_1177(
            already_fetched_urls)

        centers = sorted(centers_from_1177 + centers_from_vgr +
                         centers_from_manual_lists,
                         key=lambda k: k['name'])
        Writer.write_json(centers, 'centers.json')
