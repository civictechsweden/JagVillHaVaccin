import datetime

from urllib.request import urlopen
from bs4 import BeautifulSoup
import scrapers.elva77 as elva77

URL = 'https://vaccinationsbokning.regionvasterbotten.se/'

MONTHS = [
    'januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti',
    'september', 'oktober', 'november', 'december'
]


def last_updated(soup):
    return soup.find(class_='modified-time')


def get_slots(center):
    timeslots = {}
    available_slots = []
    amount_of_slots = 0

    for timeslot in center.find_all(class_='timeslot col-xs-4 col-sm-4'):
        date = timeslot.find(class_='timeslot-date__inner').text.strip()
        availability = timeslot.find(
            class_='col-xs-6 timeslot-availibility').text.strip()
        timeslots[date] = availability
        available_slots.append(date)

        amount_of_slots += int(timeslots[date].split()[0])

    if len(available_slots) > 0:
        next_slot = {
            'next': transform_date(available_slots[0]),
            'amount_of_slots': amount_of_slots
        }
    else:
        next_slot = {'next': None, 'amount_of_slots': 0}
    return timeslots, next_slot


def get_center_info(center):
    if not center.h3:
        return None

    vaccination_center = center.h3.text
    if vaccination_center.split()[0] in ['Vaccina', 'Central']:
        municipality = center.h3.text.split()[-1]
    else:
        municipality = center.h3.text.split()[0]
    address = center.find(class_='vaccination-center__address').text
    link = center.a['href']
    timeslots, next_slot = get_slots(center)
    return {
        'municipality': municipality,
        'vaccination_center': vaccination_center,
        'address': address,
        'latitude': '',
        'longitude': '',
        'region': '24',
        'link': link,
        'timeslots': timeslots,
        'next_slot': next_slot,
    }


def get_centers():
    html = urlopen(URL).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    results = []

    for center in soup.find_all(class_='row jumbotron'):
        center_info = get_center_info(center)
        if center_info:
            results.append(center_info)

    results = list({v['vaccination_center']: v for v in results}.values())

    return results


def transform_date(date_string):
    day = int(date_string.split(' ')[0])
    month = date_string.split(' ')[1]
    if month == 'okttober': month = 'oktober'
    month = [MONTHS.index(manad) for manad in MONTHS if manad == month][0]
    return datetime.datetime(2021, month + 1, day)


def get_center_from(centers, center_url):
    results = [
        center for center in centers if elva77.get_short_url(center['link']) ==
        elva77.get_short_url(center_url)
    ]

    if (len(results) > 0):
        return results[0]
    return None


def get_next_time_and_slots(center):
    return center['next_slot']
