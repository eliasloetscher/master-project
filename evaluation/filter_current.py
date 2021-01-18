from parameters import Parameters
from pathlib import Path
import csv
import statistics
import matplotlib.pyplot as plt


# read file
LOCATION = Parameters.LOCATION_LOG_FILES
filename = "C:/Users/eliasl/Documents/logfiles/source_test_hvamp_normal.txt"


def read_csv(file, start_row, column):

    path = Path(file)

    datapoints = []

    with open(file) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar=',')
        for n, row in enumerate(spamreader):
            if n < 11:
                continue

            datapoints.append(float(row[4]))

    return datapoints


data = read_csv(filename, 0, 0)
print(data)

# limit to decay period
data = data[22:140]

# filter moving average
average = data[0:20]
filter_list_temp = data[0:20]
print(filter_list_temp)
for i in range(10, len(data)-1):
    filter_list_temp = filter_list_temp[1:20]
    filter_list_temp.append(data[i])
    average.append(round(statistics.mean(filter_list_temp), 2))

# filter moving median
median = []
filter_list_temp = data[0:10]
print(filter_list_temp)
for i in range(10, len(data)-1):
    filter_list_temp = filter_list_temp[1:10]
    filter_list_temp.append(data[i])
    median.append(round(statistics.median(filter_list_temp), 2))


# plot
plt.plot(average)
plt.plot(data)
plt.title("Title")
plt.xlabel("Time in s")
plt.ylabel("Current in pA")
plt.grid()
plt.show()
