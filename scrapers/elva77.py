import json
import re
import urllib

from time import mktime

import scrapers.mittvaccin as mittvaccin

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
    print('Fetching info from 1177 for {}'.format(card['DisplayName']))

    adress_and_postcode = get_address_and_postcode(card)

    services = card['EServices']
    covid_vaccination_services = [
        service['Url'] for service in services
        if 'vaccination' in str.lower(service['Text'])
        or 'covid' in str.lower(service['Text'])
    ]

    url = BASE_URL + center_url

    platform_url = next(iter(covid_vaccination_services or []), None)
    platform = get_platform(platform_url)

    platform_id = None
    if platform == 'MittVaccin':
        platform_id = mittvaccin.get_id_from_url(platform_url)

    center_info = {
        'name': card.get('DisplayName'),
        'region': card.get('CountyCode'),
        '1177_url': url,
        'platform_url': platform_url,
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
        'platform': platform,
        'type': 'vaccination-center',
        '1177_id': card.get('HsaId'),
        'platform_id': platform_id,
        'vaccine_type': None,
        'appointment_by_phone_only': not is_fetchable(platform),
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


def get_platform(url):
    if not url:
        return None
    if 'https://bokning.mittvaccin.se/' in url:
        return 'MittVaccin'
    if 'https://www.vaccina.se/' in url:
        return 'Vaccina'
    if 'https://e-tjanster.1177.se/' in url: return '1177'
    if 'https://formular.1177.se/' in url: return '1177'
    if 'https://arende.1177.se/' in url: return '1177'
    else:
        return None


def is_fetchable(platform):
    if platform == 'MittVaccin': return True
    if platform == 'Vaccina': return True
    return False


def create_unlisted_center(center):
    platform_url = center['link']
    platform = get_platform(platform_url)
    platform_id = mittvaccin.get_id_from_url(
        platform_url) if platform == 'MittVaccin' else center.get('id')

    return {
        'name':
        center.get('vaccination_center'),
        'region':
        "0{}".format(int(center['region']))
        if int(center['region']) < 10 else str(center['region']),
        '1177_url':
        None,
        'platform_url':
        platform_url,
        'location': {
            'longitude': center['longitude'],
            'latitude': center['latitude'],
            'city': center['municipality'],
            'cp': match_postcode(center['address'])
        },
        'metadata': {
            'address': center['address'],
            'business_hours': None,
            'phone_number': ''
        },
        'platform':
        platform,
        'type':
        'vaccination-center',
        '1177_id':
        center.get('hsaid'),
        'platform_id':
        platform_id,
        'vaccine_type':
        None,
        'appointment_by_phone_only':
        not is_fetchable(platform),
    }
