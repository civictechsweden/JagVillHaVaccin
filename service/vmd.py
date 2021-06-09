import json
import pytz

from datetime import datetime

import scrapers.vaccina as vaccina
import scrapers.mittvaccin as mittvaccin
import scrapers.patient_nu as patient_nu
import scrapers.vgr as vgr
import scrapers.macc as macc
import scrapers.skane as skane
from service.writer import Writer
from service.dater import Dater


class VMD(object):
    @staticmethod
    def convert(region_number):
        with open('centers.json') as json_file:
            centers = json.load(json_file)

        with open('regions.json') as json_file:
            regions = json.load(json_file)

        centres_disponibles = []
        centres_indisponibles = []

        region_url = next(
            (region['1177_url']
             for region in regions if region['code'] == int(region_number)),
            None)

        region_centers = [
            center for center in centers if center['region'] == region_number
        ]

        if (region_number == '14'):
            centers_vgr = vgr.get_centers_from_API()
        elif (region_number == '12'):
            centers_macc = macc.get_centers()
            centers_1177_skane = skane.get_centers()

        for center in region_centers:
            print(center['name'])

            if center['platform'] == 'MittVaccin':
                url = center['platform_url']
                url = mittvaccin.normalise_url(url)

                next_time_and_slots = mittvaccin.get_next_time_and_slots(
                    center['platform_id'], Dater.today(), Dater.in_3_months())

                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            elif center['platform'] == 'Vaccina' and center['platform_id']:
                url = center['platform_url']
                center_id = center['platform_id']
                region_vaccina_code = vaccina.REGION_CODES[center['region']]

                next_time_and_slots = vaccina.get_next_time_and_slots(
                    region_vaccina_code, center_id, Dater.today(),
                    Dater.in_3_months())

                prochain_rdv = next_time_and_slots['next']
                appointment_count = next_time_and_slots['amount_of_slots']
            elif center['platform'] == 'Patient':
                url = center['platform_url']
                next_time_and_slots = patient_nu.get_next_time_and_slots(
                    center['platform_id'], Dater.today(), Dater.in_3_months())
            else:
                url = center['1177_url']

                prochain_rdv = None
                appointment_count = 0

            if (region_number == '14'):
                center_vgr = vgr.get_center_from(centers_vgr,
                                                 center['1177_id'])

                if (center_vgr):
                    next_time_and_slots = vgr.get_next_time_and_slots(
                        center_vgr)
                    prochain_rdv = next_time_and_slots['next']
                    appointment_count = next_time_and_slots['amount_of_slots']
            elif (region_number == '12'):
                center_1177_skane = skane.get_center_from(
                    centers_1177_skane, center['1177_id'])

                if (center_1177_skane):
                    next_time_and_slots = skane.get_next_time_and_slots(
                        center_1177_skane)
                    prochain_rdv = next_time_and_slots['next']
                    appointment_count = next_time_and_slots['amount_of_slots']

                center_macc = macc.get_center_from(centers_macc,
                                                   center['1177_id'])

                if (center_macc):
                    next_time_and_slots = macc.get_next_time_and_slots(
                        center_macc)
                    prochain_rdv = next_time_and_slots['next']
                    appointment_count = next_time_and_slots['amount_of_slots']

            if center['region'] in ['10', '06']:
                print(
                    'Replacing URL to satisfy request from Blekinge and Jönköping'
                )
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

            if appointment_count > 0:
                centres_disponibles.append(dict(vmd_center))
            else:
                centres_indisponibles.append(dict(vmd_center))

        vmd_data = {
            'version': 1,
            'last_updated': str(Dater.now()),
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
