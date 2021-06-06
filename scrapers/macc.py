from service.downloader import Downloader

BASE_URL = 'https://covidvaccinering.com/api/v1/locations/WithBookableSeats'


def get_centers():
    return Downloader.get_json(BASE_URL)


def get_next_time_and_slots(center):
    return {'next': None, 'amount_of_slots': center['bookableSeats']}


def get_center_from(centers, center_id):
    results = [center for center in centers if center['hsaid'] == center_id]
    if (len(results) > 0):
        return results[0]
    return None
