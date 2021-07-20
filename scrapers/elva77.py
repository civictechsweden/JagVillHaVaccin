import json
import re
import urllib

import scrapers.mittvaccin as mittvaccin
import scrapers.patient_nu as patient_nu

from service.downloader import Downloader

BASE_URL = 'https://www.1177.se'
ALL_COVID_CENTERS = '/hitta-vard/?caretype=Covid-19%20vaccination&batchsize='
BATCH_SIZE = 1000


def get_vaccination_centers():
    content = get_preloaded_state_content('{}{}{}'.format(
        BASE_URL, ALL_COVID_CENTERS, BATCH_SIZE))

    if not content:
        return []

    return content['SearchResult']['SearchHits']


def search_center(name):
    return Downloader.get_json('{}/api/hjv/suggest?{}'.format(
        BASE_URL, urllib.parse.urlencode({'q':
                                          name})))['Units'][0]['FriendlyUrl']


def get_id_from_url(platform_url):
    platform = get_platform(platform_url)

    if platform == 'MittVaccin':
        return mittvaccin.get_id_from_url(platform_url)
    elif platform == 'Patient':
        return patient_nu.get_id_from_url(platform_url)

    return None


def get_center_info(center_url):
    with open('regions.json') as json_file:
        regions = json.load(json_file)

    content = get_preloaded_state_content('{}{}'.format(BASE_URL, center_url))

    if not content:
        return None

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

    region_code = [
        region['code'] for region in regions
        if region['1177_name'] == card.get('County')
    ]
    if len(region_code) > 0:
        region_code = region_code[0]
        region_code = str(
            region_code) if region_code > 9 else "0" + str(region_code)
    else:
        region_code = None

    center_info = {
        'name': card.get('DisplayName'),
        'region': region_code,
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
        'platform_id': get_id_from_url(platform_url),
        'vaccine_type': None,
        'appointment_by_phone_only': not is_fetchable(platform),
    }

    if 'PhoneNumber' in card:
        center_info['metadata']['phone_number'] = card['PhoneNumber'].replace('-', '').replace(' ', '') 

    return center_info


def get_preloaded_state_content(url):
    soup = Downloader.get_html_soup(url)

    if not soup:
        return None

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
    if 'https://patient.nu/' in url:
        return 'Patient'
    if 'https://covidvaccinering.com/' in url:
        return 'MACC'
    if 'https://e-tjanster.1177.se/' in url: return '1177'
    if 'https://formular.1177.se/' in url: return '1177'
    if 'https://arende.1177.se/' in url: return '1177'
    else:
        return None


def is_fetchable(platform):
    if platform == 'MittVaccin': return True
    if platform == 'Vaccina': return True
    if platform == 'Patient': return True
    if platform == 'MACC': return True
    return False


def get_short_url(elva77_url):
    if elva77_url and BASE_URL in elva77_url:
        return '/hitta-vard/' + elva77_url.split('/hitta-vard/')[1]
    return None


def create_unlisted_center(center):
    print('Writing unlisted center {}'.format(
        center.get('vaccination_center'), ))
    platform_url = center['link']
    platform = get_platform(platform_url)

    platform_id = get_id_from_url(platform_url)
    if not platform_id:
        platform_id = center.get('id')

    longitude = center.get('longitude') if center.get('longitude') else ''
    latitude = center.get('latitude') if center.get('latitude') else ''

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
            'longitude': longitude,
            'latitude': latitude,
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
