import json
import pytz

from datetime import datetime

import scrapers.vaccina as vaccina
import scrapers.mittvaccin as mittvaccin
import scrapers.vgr as vgr
from service.writer import Writer


class VMD(object):
    @staticmethod
    def convert(region_number):
        now = str(datetime.now(pytz.timezone('Europe/Stockholm')))

        with open('centers.json') as json_file:
            centers = json.load(json_file)

        with open('regions.json') as json_file:
            regions = json.load(json_file)

        centres_disponibles = []
        centres_indisponibles = []

        region_url = next(
            (region['1177_url']
             for region in regions if region['code'] == region_number), None)

        region_centers = [
            center for center in centers if center['region'] == region_number
        ]

        if (region_number == '14'):
            centers_vgr = vgr.get_centers()

        for center in region_centers:
            print(center['name'])

            if (region_number == '14'
                    and vgr.get_center_from(centers_vgr, center['1177_id'])):
                next_time_and_slots = vgr.get_next_time_and_slots(
                    vgr.get_center_from(centers_vgr, center['1177_id']))
                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            elif center['platform'] == 'MittVaccin':
                url = center['platform_url']
                next_time_and_slots = mittvaccin.get_next_time_and_slots(
                    center['platform_id'], '210517', '210630')
                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            elif center['platform'] == 'Vaccina':
                url = center['platform_url']
                center_id = center['platform_id']
                region_vaccina_code = vaccina.REGION_CODES[center['region']]

                next_time_and_slots = vaccina.get_next_time_and_slots(
                    region_vaccina_code, center_id, '2021-05-17', '2021-06-30')

                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            else:
                url = center['1177_url']
                prochain_rdv = None
                appointment_count = 0

            url = region_url

            id = center[
                'internal_id'] if 'internal_id' in center else center.get(
                    'platform_id')
            vmd_center = {
                'departement': center['region'],
                'nom': center['name'],
                'url': url,
                'location': center['location'],
                'metadata': center['metadata'],
                'prochain_rdv': str(prochain_rdv)
                if prochain_rdv else None,  # Get from the scrapers
                'plateforme': center['platform'],
                'type': center['type'],
                'appointment_count': appointment_count,
                'internal_id': id,
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

        Writer.write_json(vmd_data, '{}.json'.format(region_number))

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
                    'nom_region': region['name'],
                    '1177_url': region['1177_url']
                }))

        Writer.write_json(vmd_regions, 'departements.json')
