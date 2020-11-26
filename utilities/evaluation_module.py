import csv
from pathlib import Path

FILE_LOCATION = "C:/Users/eliasl/Documents/logfiles/testlog.txt"


def read_csv(file, start_row, column):

    path = Path(file)

    with open(file) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar=',')
        for row in spamreader:
            ...
            print(', '.join(row))


read_csv(FILE_LOCATION, 0, 0)
