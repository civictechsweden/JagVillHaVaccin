import datetime

from urllib.request import urlopen
from bs4 import BeautifulSoup

URL = 'https://vaccinationsbokning.regionvastmanland.se/'

MONTHS = [
    'Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni', 'Juli', 'Aug',
    'Sept', 'Okt', 'November', 'December'
]


def get_center_link(center_name):
    center_name = center_name.replace(' ', '-')
    for char in center_name:
        if char in 'öÖ':
            center_name = center_name.replace(char, 'o')
        if char in 'åäÅÄ':
            center_name = center_name.replace(char, 'a')

    return 'https://www.1177.se/hitta-vard/kontaktkort/' + center_name


def get_coordinates(center):
    coordinates = center.find(class_='icon-map-pin-plus')['href'].split('=')[2]
    latitude = coordinates.split(',')[0]
    longitude = coordinates.split(',')[1]
    return latitude, longitude


def get_next_available_slot(center):
    timeslots = {}
    available_slots = []
    for timeslot in center.find_all(class_='timeslot col-xs-4 col-sm-4'):
        date = timeslot.find(class_='timeslot-date__inner').text.strip()
        availability = timeslot.find(
            class_='col-xs-6 timeslot-availibility').text.strip()
        timeslots[date] = availability
        if availability == 'Ledigt':
            available_slots.append(date)

    if len(available_slots) > 0:
        next_slot = {
            'next': transform_date(available_slots[0]),
            'amount_of_slots': None
        }
    else:
        next_slot = {'next': None, 'amount_of_slots': 0}
    return next_slot


def get_center_info(center):
    vaccination_center = center.h3.text
    municipality = center.h3.text.split()[0]
    address = center.find(class_='vaccination-center__address').text
    latitude, longitude = get_coordinates(center)
    link = get_center_link(vaccination_center)
    next_slot = get_next_available_slot(center)
    return {
        'municipality': municipality,
        'vaccination_center': vaccination_center,
        'address': address,
        'latitude': float(latitude),
        'longitude': float(longitude),
        'region': '19',
        'link': link,
        'next_slot': next_slot
    }


def get_centers():
    html = urlopen(URL).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    results = []

    for center in soup.find_all(class_='row jumbotron'):
        center_info = get_center_info(center)
        results.append(center_info)

    return results


def transform_date(date_string):
    day = int(date_string.split(' ')[0])
    month = date_string.split(' ')[1]
    month = [MONTHS.index(manad) for manad in MONTHS if manad == month][0]
    return datetime.datetime(2021, month + 1, day)


def get_center_from(centers, center_url):
    results = [center for center in centers if center['link'] == center_url]
    if (len(results) > 0):
        return results[0]
    return None


def get_next_time_and_slots(center):
    return center['next_slot']
