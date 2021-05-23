from datetime import datetime
import json
import re
from sys import platform
import urllib

from time import mktime

from service.downloader import Downloader

BASE_URL = 'https://www.1177.se'
ALL_COVID_CENTERS = '/hitta-vard/?caretype=Covid-19%20vaccination&batchsize='
BATCH_SIZE = 500


def get_vaccination_centers():
    content = get_preloaded_state_content('{}{}{}'.format(
        BASE_URL, ALL_COVID_CENTERS, BATCH_SIZE))

    return content['SearchResult']['SearchHits']


def search_center(name):
    return Downloader.get_json('{}/api/hjv/suggest?{}'.format(
        BASE_URL, urllib.parse.urlencode({'q':
                                          name})))['Units'][0]['FriendlyUrl']


def get_center_url(center):
    return center['Url']


def get_center_info(center_url):
    content = get_preloaded_state_content('{}{}'.format(BASE_URL, center_url))

    card = content['Card']
    print(card['DisplayName'])

    adress_and_postcode = get_address_and_postcode(card)

    services = card['EServices']
    covid_vaccination_services = [
        service['Url'] for service in services
        if 'vaccination' in str.lower(service['Text'])
        or 'covid' in str.lower(service['Text'])
    ]

    vaccination_url = BASE_URL + center_url

    if len(covid_vaccination_services) > 0:
        vaccination_url = covid_vaccination_services[0]

    center_info = {
        'name': card.get('DisplayName'),
        'region': card.get('CountyCode'),
        'url': vaccination_url,
        'location': {
            'longitude':
            card['Location'].get('longitude') if 'Location' in card else None,
            'latitude':
            card['Location'].get('latitude') if 'Location' in card else None,
            'city':
            card.get('Municipality'),
            'cp':
            adress_and_postcode['postcode']
        },
        'metadata': {
            'address': adress_and_postcode['address'],
            'business_hours': None,
        },
        'platform': get_platform(vaccination_url),
        'type': 'vaccination-center',
        'internal_id': card.get('HsaId'),
        'vaccine_type': None,
        'appointment_by_phone_only': False,
    }

    if 'PhoneNumber' in card:
        center_info['metadata']['phone_number'] = card['PhoneNumber']

    return center_info


def get_preloaded_state_content(url):
    soup = Downloader.get_html_soup(url)
    soup_text = str(soup)
    start = soup_text.index('{"__PRELOADED_STATE__":')
    end = soup_text.index('.__PRELOADED_STATE__</script>')

    preloaded_state = json.loads(soup_text[start:end])

    return preloaded_state['__PRELOADED_STATE__']['Content']


def get_address_and_postcode(card):
    address = card.get('Address')

    if address:
        postcode = match_postcode(address)
        if postcode == 00000 and 'PostalAddress' in card:
            postcode = match_postcode(card['PostalAddress'])
    elif 'PostalAddress' in card:
        address = card.get('PostalAddress')
        postcode = match_postcode(address)
    else:
        address = ''
        postcode = 00000

    return {'address': address, 'postcode': postcode}


def match_postcode(address):
    postcode_matches = re.search('[0-9]{5}', address)
    if (postcode_matches):
        return postcode_matches.group(0)

    postcode_matches = re.search('[0-9]{3}\s[0-9]{2}', address)
    if (postcode_matches):
        return postcode_matches.group(0).replace(' ', '')

    return '00000'


def get_platform(vaccination_url):
    if 'https://bokning.mittvaccin.se/' in vaccination_url:
        return 'MittVaccin'  #'MittVaccin' (Testing with an existing platform on the frontend)
    if 'https://e-tjanster.1177.se/' in vaccination_url: return '1177'
    if 'https://formular.1177.se/' in vaccination_url: return '1177'
    if 'https://arende.1177.se/' in vaccination_url: return '1177'
    if 'https://www.1177.se/hitta-vard/kontaktkort/' in vaccination_url:
        return None


def create_unlisted_center(name, region, address, url):
    return {
        'name': name,
        'region': region,
        'url': url,
        'location': None,
        'metadata': {
            'address': address,
            'business_hours': None,
            'phone_number': None
        },
        'platform': get_platform(url),
        'type': 'vaccination-center',
        'internal_id': None,
        'vaccine_type': None,
        'appointment_by_phone_only': False,
    }
