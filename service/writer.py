import csv


class Writer(object):
    @staticmethod
    def write(next_available_slots, filename):
        keys = next_available_slots[0].keys()

        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(next_available_slots)
