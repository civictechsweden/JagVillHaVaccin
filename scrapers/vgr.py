import os
import re

from service.downloader import Downloader

VACCINATIONSTIDER_URL = 'https://www.vgregion.se/ov/vaccinationstider/vaccinationstider/'
BOKNINGSBARA_TIDER_URL = 'https://www.vgregion.se/ov/vaccinationstider/bokningsbara-tider/'

NUMBER_OF_WEEKS = 12
API_URL = 'https://api.vgregion.se/e-crm-scheduling-public/api/v1/testCenter?numberWeeks={}'.format(
    NUMBER_OF_WEEKS)

HEADERS = {
    'client_id': os.environ['VGR_CLIENT_ID'],
    'client_secret': os.environ['VGR_CLIENT_SECRET']
}


def get_centers_from_API():
    return Downloader.get_json_with_headers(API_URL, HEADERS)['testcenters']


def get_municipalities():
    soup = Downloader.get_html_soup(VACCINATIONSTIDER_URL)
    lis = soup.find_all('li', 'block__row media')

    municipalities = []
    for li in lis:
        a = li.select('div > div > a')[0]
        municipalities.append({'name': a.string, 'url': a.get('href')})

    return municipalities


def get_centers():
    municipalities = get_municipalities()

    centers = []

    for municipality in municipalities:
        print('Getting centers for {}'.format(municipality['name']))
        soup = Downloader.get_html_soup(municipality['url'])

        lis = soup.find_all('li', 'mottagningblock')

        for li in lis:
            name = li.select('div > div > div > div > h3')

            if len(name) > 0:
                name = name[0]

                link_block = li.select('div > div > div > ul > li')[0]
                a = link_block.select('a')[0]
                span = link_block.select('span')

                if len(span) == 0:
                    amount = 0
                else:
                    text = span[0].string
                    if 'inga' in text.lower():
                        amount = 0
                    else:
                        text = text.split('lediga tider')[0]
                        amount = int(re.findall(r'\b\d+\b', text)[0])
                centers.append({
                    'municipality': municipality['name'],
                    'name': name.string,
                    'url': a.get('href'),
                    'amount_of_slots': amount
                })

    return centers


def get_center_from(centers, center_id):
    results = [center for center in centers if center['hsaid'] == center_id]
    if (len(results) > 0):
        return results[0]
    return None


def convert_center(center):
    return {
        'region': '14',
        'vaccination_center': center['title'],
        'link': center['urlBooking'],
        'hsaid': center['hsaid'],
        'municipality': '',
        'address': '',
        'latitude': '',
        'longitude': ''
    }


def get_next_time_and_slots(center):
    amount_of_slots = center['timeslots']
    if not amount_of_slots:
        amount_of_slots = 0
    return {'next': None, 'amount_of_slots': amount_of_slots}
