from datetime import datetime
import time
from time import mktime

from service.downloader import Downloader

BASE_URL = 'https://booking-api.mittvaccin.se/clinique/'


def get_appointment_types(id):
    return Downloader.get_json('{}{}/appointmentTypes'.format(BASE_URL, id))


def get_slots(id, appointment_type_id, start_date, end_date):
    url = '{}{}/appointments/{}/slots/{}-{}'.format(BASE_URL, id,
                                                    appointment_type_id,
                                                    start_date, end_date)
    return Downloader.get_json(url)


def get_next_time_and_slots(id, start_date, end_date):
    types = get_appointment_types(id)
    types_id = [type['id'] for type in types]

    all_available_slots = []

    for type_id in types_id:
        days = get_slots(id, type_id, start_date, end_date)

        for day in days:
            slots = day['slots']
            available_slots = [
                slot['when'] for slot in slots if slot['available']
            ]
            if len(available_slots) > 0:
                available_slots = {
                    'day': day['date'],
                    'times': available_slots
                }
                all_available_slots.append(dict(available_slots))

    if len(all_available_slots) > 0:
        next_slot = all_available_slots[0]
        next_slot = date_from(next_slot['day'], next_slot['times'][0])

        amount_of_slots = 0

        for day in all_available_slots:
            amount_of_slots += len(day['times'])

        return {'next': next_slot, 'amount_of_slots': amount_of_slots}

    return {'next': None, 'amount_of_slots': 0}


def get_id_from_url(url):
    id = url.replace('https://bokning.mittvaccin.se/klinik/', '')
    id = id.replace('/bokning', '')
    id = id.replace('/min-bokning', '')
    return id


def date_from(slotDate, slotTime):
    struct = time.strptime('{}{}'.format(slotDate, slotTime), "%y%m%d%H:%M")
    return datetime.fromtimestamp(mktime(struct))
