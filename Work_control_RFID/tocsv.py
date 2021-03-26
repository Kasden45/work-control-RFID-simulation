import csv

"""Creates report from sql query"""


def create_report(table_of_dictionaries, name):
    # Tablica kluczy słownika z zapytania SQL
    fnames = ["card_id", "employee_id", "firstname", "lastname", "start_time", "finish_time", "work_time"]
    f = open('%s.csv' % (name), 'w', newline='')
    with f:
        writer = csv.writer(f)
        writer.writerow(fnames)  # Insert columns names
        for row in table_of_dictionaries:  # Inert values
            writer.writerow(row)
