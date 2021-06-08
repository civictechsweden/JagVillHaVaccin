import json
import pandas as pd
from service.writer import Writer

with open('regions.json') as regions_json:
    regions = json.load(regions_json)

output = {}
centre_count = 0
supported_centre_count = 0
dose_count = 0

for region in regions:

    with open(region['code'] + '.json') as region_json:
        appointments = json.load(region_json)

    # Number of vaccination centres that have available vaccines
    centre_count_by_region = len(appointments['centres_disponibles'])
    centre_count += centre_count_by_region

    # Number of vaccine doses available

    df_appointments = pd.DataFrame.from_dict(appointments['centres_disponibles'])
    if not df_appointments.empty:
        dose_count_by_region = df_appointments['appointment_count'].sum()
        dose_count += dose_count_by_region
    else:
        dose_count_by_region = 0

    # Number of vaccination centres supported
    df_all_centres = df_appointments.append(pd.DataFrame.from_dict(appointments['centres_indisponibles']), ignore_index=True)
    if not df_all_centres.empty:
        supported_centre_count_by_region = (~df_all_centres['appointment_by_phone_only']).sum()
        supported_centre_count += supported_centre_count_by_region
    else:
        supported_centre_count_by_region = 0

    output[region['code']] = {
        'disponibles': int(centre_count_by_region),
        'total': int(supported_centre_count_by_region),
        'creneaux': int(dose_count_by_region),
    }

output['tout_departement'] = {
    'disponibles': int(centre_count),
    'total': int(supported_centre_count),
    'creneaux': int(dose_count),
}

Writer.write_json(output, 'data/output/stats.json')
