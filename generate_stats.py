import json
import pandas as pd
from service.writer import Writer

with open('departements.json') as regions_json:
    regions = json.load(regions_json)

stats = {}
centre_count = 0
supported_centre_count = 0
dose_count = 0
info_centres = {}

for region in regions:
    region_code = region['code_departement']
    # if len(str(region_code)) < 2:
    #     region_code = '0{}'.format(region_code)
    
    with open('{}.json'.format(region_code)) as region_json:
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

    stats[region_code] = {
        'disponibles': int(centre_count_by_region),
        'total': int(supported_centre_count_by_region),
        'creneaux': int(dose_count_by_region),
    }
    print(appointments)
    info_centres[region_code] = appointments




stats['tout_departement'] = {
    'disponibles': int(centre_count),
    'total': int(supported_centre_count),
    'creneaux': int(dose_count),
}
print(info_centres)
Writer.write_json(stats, 'data/output/stats.json')
Writer.write_json(info_centres, 'data/output/info_centres.json')