from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

URL = 'https://vaccinationsbokning.regionvastmanland.se/'

html = urlopen(URL).read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

results = []

for center in soup.find_all(class_='row jumbotron'):

    municipality = center.h3.text.split()[0]
    vaccination_center = center.h3.text
    address = center.find(class_='vaccination-center__address').text
    attributes = center.h3.a['href'].split('=')[2]
    latitude = float(attributes.split(',')[0])
    longitude = float(attributes.split(',')[1])

    timeslots = {}
    available_slots = []

    for timeslot in center.find_all(class_='timeslot col-xs-4 col-sm-4'):
        date = timeslot.find(class_='timeslot-date__inner').text.strip()
        availability = timeslot.find(
            class_='col-xs-6 timeslot-availibility').text.strip()
        timeslots[date] = availability
        if timeslots[date] == 'Ledigt':
            available_slots.append(date)
    if len(available_slots) > 0:
        next_slot = available_slots[0]
    else:
        next_slot = None

    center_info = {
        'municipality': municipality,
        'vaccination_center': vaccination_center,
        'address': address,
        'latitude': latitude,
        'longitude': longitude,
        'region': '19',
        'timeslots': timeslots,
        'next_slot': next_slot,
    }

    results.append(center_info)

with open('vastmanland.json', 'w') as jf:
    json.dump(results, jf, ensure_ascii=False, indent=4)
