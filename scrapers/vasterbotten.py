
from urllib.request import urlopen
from bs4 import BeautifulSoup


URL = 'https://vaccinationsbokning.regionvasterbotten.se/'

html = urlopen(URL).read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')


def last_updated():
    return soup.find(class_='modified-time')


def get_slots(center):
    timeslots = {}
    available_slots = []
    for timeslot in center.find_all(class_='timeslot col-xs-4 col-sm-4'):
        date = timeslot.find(class_='timeslot-date__inner').text.strip()
        availability = timeslot.find(
            class_='col-xs-6 timeslot-availibility').text.strip()
        timeslots[date] = availability
        available_slots.append(date)

    if len(available_slots) > 0:
        next_slot = {
            'next': available_slots[0],
            'amount_of_slots': int(timeslots[available_slots[0]].split()[0])}
    else:
        next_slot = {'next': None, 'amount_of_slots': 0}
    return timeslots, next_slot


def get_center_info(center):
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
        'region': '19',
        'link': link,
        'timeslots': timeslots,
        'next_slot': next_slot,
    }


results = []
for center in soup.find_all(class_='row jumbotron'):
    center_info = get_center_info(center)
    results.append(center_info)
