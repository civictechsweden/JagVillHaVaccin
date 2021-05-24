import json
import pytz

from datetime import datetime

import scrapers.vaccina as vaccina
import scrapers.mittvaccin as mittvaccin
import scrapers.elva77 as elva77
from service.writer import Writer


class VMD(object):
    @staticmethod
    def convert(region):
        now = str(datetime.now(pytz.timezone('Europe/Stockholm'))) + '+02:00'

        with open('centers.json') as json_file:
            centers = json.load(json_file)

        centres_disponibles = []
        centres_indisponibles = []

        region_centers = [
            center for center in centers if center['region'] == region
        ]

        for center in region_centers:
            print(center['name'])

            if center['platform'] == 'MittVaccin':
                next_time_and_slots = mittvaccin.get_next_time_and_slots(
                    mittvaccin.get_id_from_url(center['url']), '210517',
                    '210630')
                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            elif center['platform'] == 'Vaccina':
                id = center['internal_id']
                region_code = vaccina.REGION_CODES[center['region']]

                next_time_and_slots = vaccina.get_next_time_and_slots(
                    region_code, id, '2021-05-17', '2021-06-30')

                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            else:
                prochain_rdv = None
                appointment_count = 0

            vmd_center = {
                'departement': center['region'],
                'nom': center['name'],
                'url': center['url'],
                'location': center['location'],
                'metadata': center['metadata'],
                'prochain_rdv': str(prochain_rdv)
                if prochain_rdv else None,  # Get from the scrapers
                'plateforme': center['platform'],
                'type': center['type'],
                'appointment_count': appointment_count,
                'internal_id': center['internal_id'],
                'vaccine_type': center['vaccine_type'],
                'appointment_by_phone_only':
                center['appointment_by_phone_only'],
                'erreur': None,
                'last_scan_with_availabilities': None,
                'request_counts': None,
                'appointment_schedules': [],
                'gid': None
            }

            if prochain_rdv:
                centres_disponibles.append(dict(vmd_center))
            else:
                centres_indisponibles.append(dict(vmd_center))

        vmd_data = {
            'version': 1,
            'last_updated': now,
            'last_scrap': [],
            'centres_disponibles': centres_disponibles,
            'centres_indisponibles': centres_indisponibles
        }

        Writer.write_json(vmd_data, '{}.json'.format(region))

    def convert_regions():
        with open('regions.json') as json_file:
            regions = json.load(json_file)

        vmd_regions = []

        for region in regions:
            vmd_regions.append(
                dict({
                    'code_departement': region['code'],
                    'nom_departement': region['name'],
                    'code_region': int(region['code']),
                    'nom_region': region['name']
                }))

        Writer.write_json(vmd_regions, 'departements.json')
