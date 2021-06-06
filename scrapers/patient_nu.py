from datetime import datetime
import time
from time import mktime

from service.downloader import Downloader

BASE_URL = 'https://patient.nu/portal/public/gettimes/'
DATE_STRUCT = "%Y-%m-%d"

NO_SLOTS = {'next': None, 'amount_of_slots': 0}


def get_slots(id, start_date, end_date):
    start = start_date.strftime(DATE_STRUCT)
    end = end_date.strftime(DATE_STRUCT)

    url = '{}{}?start={}&end={}'.format(BASE_URL, id, start, end)

    headers = {
        'User-Agent': 'PostmanRuntime/7.28.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    return Downloader.get_json_with_headers(url, headers)


def get_next_time_and_slots(id, start_date, end_date):
    slots = get_slots(id, start_date, end_date)

    available_slots = []

    if slots != []:
        for slot in slots:
            if 'Bokad' not in slot['title']:
                available_slots.append(date_from(slot['start']))

    return {
        'next': available_slots[0] if len(available_slots) > 0 else None,
        'amount_of_slots': len(available_slots)
    }


def get_id_from_url(url):
    return url.replace('https://patient.nu/portal/public/calendar/', '')


def date_from(date_and_time):
    struct = time.strptime(date_and_time, "%Y-%m-%dT%H:%M:%S.000000Z")
    return datetime.fromtimestamp(mktime(struct))
