from datetime import datetime
import time
from time import mktime

from service.downloader import Downloader

BASE_URL = 'https://apibk.cliento.com/api/v2/partner/cliento/'

REGION_CODES = {
    '04': '6YoV801j3oiq2bf5pSb92o',
    '12': '4mfh5wH5yJpGVZjk80z50D',
    '24': '3MixbkPGwjvYiq9mIJ6uh4',
    '14': 'jhW383SJEEIOe9FMtAp9h',
    '07': '2aXA6s8FXaABTWdjauuNzE'
}


def get_slots(region_id, center_id, start_date, end_date):
    url = '{}{}/resources/slots?srvIds={}&fromDate={}&toDate={}'.format(
        BASE_URL, region_id, center_id, start_date, end_date)
    return Downloader.get_json(url)['resourceSlots']


def get_next_time_and_slots(region_id, center_id, start_date, end_date):
    resource_slots = get_slots(region_id, center_id, start_date, end_date)

    all_available_slots = []

    for resource_slot in resource_slots:
        slots = resource_slot['slots']
        if len(slots) > 0:
            available_slots = [
                slot['date'] + ' ' + slot['time'] for slot in slots
            ]
            all_available_slots = all_available_slots + available_slots

    if len(all_available_slots) > 0:

        all_available_slots.sort()

        next_slot = date_from(all_available_slots[0])
        amount_of_slots = len(all_available_slots)

        return {'next': next_slot, 'amount_of_slots': amount_of_slots}

    return {'next': None, 'amount_of_slots': 0}


def get_id_from_url(url):
    id = url.replace('https://bokning.mittvaccin.se/klinik/', '')
    id = id.replace('/bokning', '')
    id = id.replace('/min-bokning', '')
    return id


def date_from(date_and_time):
    struct = time.strptime(date_and_time, "%Y-%m-%d %H:%M:%S")
    return datetime.fromtimestamp(mktime(struct))
