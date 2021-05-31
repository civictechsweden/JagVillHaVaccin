import os

from service.downloader import Downloader

NUMBER_OF_WEEKS = 8
API_URL = 'https://api.vgregion.se/e-crm-scheduling-public/api/v1/testCenter?numberWeeks={}'.format(
    NUMBER_OF_WEEKS)

HEADERS = {
    'client_id': os.environ['VGR_CLIENT_ID'],
    'client_secret': os.environ['VGR_CLIENT_SECRET']
}


def get_data():
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
