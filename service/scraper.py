import json
import string
from os import replace

import scrapers.mittvaccin as mittvaccin
import scrapers.elva77 as elva77
import scrapers.vgr as vgr
import scrapers.vasterbotten as vasterbotten
import scrapers.vastmanland as vastmanland

from service.writer import Writer


class Scraper(object):
    def scrape_centers_from_1177(already_fetched_urls):
        centers = elva77.get_vaccination_centers()

        centers_json = []

        for center in centers:
            url = elva77.BASE_URL + center['Url']

            if url not in already_fetched_urls:
                center_json = elva77.get_center_info(center['Url'])

                if center_json:
                    centers_json.append(dict(center_json))
            else:
                print('Center already fetched: {}'.format(url))

        return centers_json

    def scrape_centers_from_manual_lists():

        regions = [
            'vastragotaland', 'vasternorrland', 'blekinge', 'dalarna',
            'jonkoping', 'kalmar', 'kronoberg', 'orebro', 'skane',
            'sodermanland', 'vasterbotten', 'vastragotaland'
        ]

        centers_json = []

        for region in regions:
            print('Fetching centers from manual list for region {}'.format(
                region))
            with open('centers/' + region + '.json') as json_file:
                region_centers = json.load(json_file)

                for center in region_centers:
                    if 'address' in center and center['address'] != '':
                        centers_json.append(
                            elva77.create_unlisted_center(center))
                    else:
                        url = elva77.search_center(
                            center['vaccination_center'] + ' ' +
                            str(center.get('municipality')))

                        if url:
                            center_info = elva77.get_center_info(url)

                            if center_info:
                                center_info = dict(center_info)

                                if center['link'] != '':
                                    center_info['platform_url'] = center[
                                        'link']
                                    platform = elva77.get_platform(
                                        center['link'])
                                    center_info['platform'] = platform

                                    platform_id = elva77.get_id_from_url(
                                        center['link'])
                                    if platform_id:
                                        center_info[
                                            'platform_id'] = platform_id

                                    center_info[
                                        'appointment_by_phone_only'] = not elva77.is_fetchable(
                                            platform)

                                if 'category' in center and center[
                                        'category'] != '':
                                    center_info['name'] = '{} ({})'.format(
                                        center_info['name'],
                                        center['category'])

                                if 'id' in center and center['id'] != '':
                                    center_info['platform_id'] = center['id']

                                centers_json.append(center_info)
                        else:
                            print("Couldn't find {} on 1177".format(
                                center['vaccination_center']))

        return centers_json

    def scrape_centers_from_vgr(already_fetched_urls):
        centers = vgr.get_centers_from_API()

        centers_json = []

        for center in centers:
            url = center['urlContactCard']

            if elva77.BASE_URL in url:
                short_url = url.replace(elva77.BASE_URL + '/Vastra-Gotaland',
                                        '')

                if url not in already_fetched_urls:
                    center_json = elva77.get_center_info(short_url)

                else:
                    print('Center already fetched: {}'.format(url))

            else:
                center_json = elva77.create_unlisted_center(
                    vgr.convert_center(center))

            if center_json:
                center_json['appointment_by_phone_only'] = False
                centers_json.append(dict(center_json))

        return centers_json

    def scrape_centers_from_vasterbotten(already_fetched_urls):
        centers = vasterbotten.get_centers()

        centers_json = []

        for center in centers:
            url = center['link']

            if elva77.BASE_URL in url:
                short_url = url.replace(elva77.BASE_URL + '/Vasterbotten', '')

                if url not in already_fetched_urls:
                    center_json = elva77.get_center_info(short_url)

                else:
                    print('Not fetching this one: {}'.format(url))

            else:
                center_json = elva77.create_unlisted_center(center)

            if center_json:
                center_json['appointment_by_phone_only'] = False
                centers_json.append(dict(center_json))

        return centers_json

    def scrape_centers_from_vastmanland(already_fetched_urls):
        centers = vastmanland.get_centers()

        centers_json = []

        for center in centers:
            url = center['link']

            if elva77.BASE_URL in url:
                short_url = url.replace(elva77.BASE_URL, '')

                if url not in already_fetched_urls:
                    center_json = elva77.get_center_info(short_url)

                else:
                    print('Center already fetched: {}'.format(url))

            else:
                center_json = center

            if center_json:
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

        centers_from_vasterbotten = Scraper.scrape_centers_from_vasterbotten(
            already_fetched_urls)

        already_fetched_urls = already_fetched_urls + [
            center['1177_url']
            for center in centers_from_vasterbotten if '1177_url' in center
        ]

        centers_from_vastmanland = Scraper.scrape_centers_from_vastmanland(
            already_fetched_urls)

        already_fetched_urls = already_fetched_urls + [
            center['1177_url']
            for center in centers_from_vastmanland if '1177_url' in center
        ]

        centers_from_1177 = Scraper.scrape_centers_from_1177(
            already_fetched_urls)

        centers = centers_from_1177 + centers_from_vgr + centers_from_vasterbotten + centers_from_vastmanland + centers_from_manual_lists

        Writer.write_json(centers, 'centers.json')
