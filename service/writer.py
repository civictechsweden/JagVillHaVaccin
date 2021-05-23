import csv
import json


class Writer(object):
    @staticmethod
    def write_csv(next_available_slots, filename):
        keys = next_available_slots[0].keys()

        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(next_available_slots)

    def write_json(dict, filename):
        with open(filename, 'w') as fp:
            json_string = json.dumps(dict, ensure_ascii=False).encode('utf-8')
            fp.write(json_string.decode())
