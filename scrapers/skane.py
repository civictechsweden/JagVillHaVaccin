import os
import re

from service.downloader import Downloader

LEDIGA_TIDER_URL = 'https://www.skane.se/Halsa-och-vard/hitta-vard/covid-19-coronavirus/fragor-och-svar-om-covid-19-vaccination/lediga-tider-for-vaccination-mot-covid-19/'


def get_centers():
    soup = Downloader.get_html_soup(LEDIGA_TIDER_URL)
    divs = soup.find_all('div', 'municipality-area')

    centers = []

    for div in divs:
        center_divs = div.select('div.vaccination-clinic-area')

        for center_div in center_divs:
            spans = center_div.select('span')

            name = spans[0].string.strip()
            a = center_div.select('a')

            if len(a) > 0:
                url = a[0].get('href')
            else:
                url = ''

            if len(spans) == 1 or url == '':
                amount = 0
            else:
                text = spans[1].string
                amount = int(re.findall(r'\d+\b', text)[0])

            if 'hsaid' in url:
                hsaid = url.split('hsaid=')[1].split('&')[0]
            else:
                hsaid = None

            centers.append({
                'municipality': div.select('h3 > span')[0].string,
                'name': name,
                'url': url,
                'hsaid': hsaid,
                'amount_of_slots': amount
            })

    return centers


def get_center_from(centers, center_id):
    results = [
        center for center in centers if center.get('hsaid') == center_id
    ]
    if (len(results) > 0):
        return results[0]
    return None


def convert_center(center):
    return {
        'region': '12',
        'vaccination_center': center['title'],
        'link': center['urlBooking'],
        'hsaid': center['hsaid'],
        'municipality': '',
        'address': '',
        'latitude': '',
        'longitude': ''
    }


def get_next_time_and_slots(center):
    amount_of_slots = center['amount_of_slots']
    if not amount_of_slots:
        amount_of_slots = 0
    return {'next': None, 'amount_of_slots': amount_of_slots}
