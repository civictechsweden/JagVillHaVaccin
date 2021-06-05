
from urllib.request import urlopen
from bs4 import BeautifulSoup


URL = 'https://vaccinationsbokning.regionvastmanland.se/'

html = urlopen(URL).read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')


def get_center_link(center_name):
    center_name = center_name.replace(' ', '-')
    for char in center_name:
        if char in 'öÖ':
            center_name = center_name.replace(char, 'o')
        if char in 'åäÅÄ':
            center_name = center_name.replace(char, 'a')

    base_url = 'https://www.1177.se/Vasterbotten/hitta-vard/kontaktkort/'
    center_link = base_url + center_name
    return center_link


def get_coordinates(center):
    coordinates = center.h3.a['href'].split('=')[2]
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
        next_slot = available_slots[0]
    else:
        next_slot = None
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


results = []
for center in soup.find_all(class_='row jumbotron'):
    center_info = get_center_info(center)
    results.append(center_info)
