import json

from service.downloader import Downloader

API_URL = 'https://test.api.vgregion.se/e-crm-scheduling-public/api/v1/testCenter'

HEADERS = {
    'client_id': '5b3cdb5c69cb472dbae3e722b2954985',
    'client_secret': 'b578dB43851442508ead6cDb92c2FD0e'
}


def get_data():
    print('teast')
    return Downloader.get_json_with_headers(API_URL, HEADERS)


def get_centers():
    return get_data()['testcenters']


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
