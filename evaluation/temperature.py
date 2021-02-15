import csv
import statistics
import numpy
import matplotlib.pyplot as plt
from pathlib import Path

FILE_LOCATION_30 = "Z:/stud/eliasl/public/data/test_setup_validation/temperature/temp_test_30gradc_15h_mcr_4tc.csv"
FILE_LOCATION_55 = "Z:/stud/eliasl/public/data/test_setup_validation/temperature/temp_test_55gradc_15h_mcr_4tc.csv"
FILE_LOCATION_80 = "Z:/stud/eliasl/public/data/test_setup_validation/temperature/temp_test_80gradc_15h_mcr_4tc.csv"
FILE_LOCATION_105 = "Z:/stud/eliasl/public/data/test_setup_validation/temperature/temp_test_105gradc_15h_mcr_4tc.csv"
FILE_LOCATION_130 = "Z:/stud/eliasl/public/data/test_setup_validation/temperature/temp_test_130gradc_15h_mcr_4tc.csv"
FILE_LOCATIONS = [FILE_LOCATION_30, FILE_LOCATION_55, FILE_LOCATION_80, FILE_LOCATION_105, FILE_LOCATION_130]

# row order according to channels in csv files. 1) surface, 2) air, 3) electrode
SENSOR_30 = [1, 3, 2]
SENSOR_55 = [2, 1, 3]
SENSOR_80 = [1, 2, 3]
SENSOR_105 = [3, 2, 1]
SENSOR_130 = [1, 3, 2]
SENSORS = [SENSOR_30, SENSOR_55, SENSOR_80, SENSOR_105, SENSOR_130]


def read_csv(file, start_row, column):

    path = Path(file)

    time = []
    time_absolute = []
    temp_row_one = []
    temp_row_two = []
    temp_row_three = []

    with open(file) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar=',')
        for row in spamreader:
            time.append(row[0])
            time_absolute.append(row[1])
            temp_row_one.append(row[2])
            temp_row_two.append(row[3])
            temp_row_three.append(row[4])
            # print(', '.join(row))
    return [time, time_absolute, temp_row_one, temp_row_two, temp_row_three]


def steady_state(temp, dev):

    # one hour in time steps (6 measurements per minute)
    timedelta = 6 * 60

    # startindex
    index = 3

    while len(temp) > index + timedelta:

        elements_one = [temp[index], temp[index+1], temp[index+2]]
        elements_two = [temp[index+timedelta], temp[index+1+timedelta], temp[index+2+timedelta]]

        elements_one_float = []
        for element in elements_one:
            elements_one_float.append(float(element[1:len(element) - 1]))

        elements_two_float = []
        for element in elements_two:
            elements_two_float.append(float(element[1:len(element) - 1]))

        element_one_float = statistics.mean(elements_one_float)
        element_two_float = statistics.mean(elements_two_float)

        if abs(element_two_float - element_one_float) < dev:
            # print("FOUND STEADY STATE AT INDEX: ", index)
            # print(element_one_float, element_two_float)
            steady_state_time = (index-2)*10/60/60
            return steady_state_time
        index += 1

    return "not found"


def calculate_delta(temp_list, dev, control_temp):

    # get time at which steady state is reached
    steady_state_time = steady_state(temp_list, dev)

    # calculate index:
    steady_state_index = int(steady_state_time*60*60/10 + 2)

    # build list for averaging (values 1 hour after steady state), note: 6 measurements per minute
    avg_list = []
    for i in range(6*60):
        element = temp_list[steady_state_index+i]
        element_float = float(element[1:len(element) - 1])
        avg_list.append(element_float)

    # calculate average
    average = statistics.mean(avg_list)

    # return delta
    return control_temp - average


def steady_state_evaluation():

    titles = ["30 °C", "55 °C", "80 °C", "105 °C", "130 °C"]
    for i in range(5):
        # get csv results
        result = read_csv(FILE_LOCATIONS[i], 0, 0)

        # match to temps
        sensors = SENSORS[i]
        temp_surface = result[sensors[0]+1]
        temp_air = result[sensors[1]+1]
        temp_electrode = result[sensors[2]+1]

        # set deviation
        deviation = 0.05

        # determine steady states
        print("-------------------------------------------")
        print("Temperature: ", titles[i])
        print("surface steady state in h: ", steady_state(temp_surface, deviation))
        print("air steady state in h: ", steady_state(temp_air, deviation))
        print("electrode steady state in h: ", steady_state(temp_electrode, deviation))
        print("-------------------------------------------\n")


def control_temp_delta_evaluation():

    titles = ["30 °C", "55 °C", "80 °C", "105 °C", "130 °C"]
    control_temperatures = [30, 55, 80, 105, 130]
    for i in range(5):

        # get csv results
        result = read_csv(FILE_LOCATIONS[i], 0, 0)

        # match to temps
        sensors = SENSORS[i]
        temp_surface = result[sensors[0] + 1]
        temp_air = result[sensors[1] + 1]
        temp_electrode = result[sensors[2] + 1]

        # set deviation
        deviation = 0.05

        # determine deltas
        print("-------------------------------------------")
        print("Temperature: ", titles[i])
        print("surface delta in °C: ", calculate_delta(temp_surface, deviation, control_temperatures[i]))
        print("air delta in °C: ", calculate_delta(temp_air, deviation, control_temperatures[i]))
        print("electrode delta in °C: ", calculate_delta(temp_electrode, deviation, control_temperatures[i]))
        print("-------------------------------------------\n")


def create_lookup_plot():
    temp_points = [30, 55, 80, 105, 130]
    delta_surface = [2.04, 4.04, 7.01, 11.01, 14.64]
    delta_air = [2.89, 6.37, 12.16, 15.41, 18.52]
    delta_electrode = [3.08, 7.24, 13.28, 15.75, 20.80]

    # calculate coefficients for interpolation
    delta_surface_fit = numpy.polyfit(temp_points, delta_surface, 1)
    delta_air_fit = numpy.polyfit(temp_points, delta_air, 1)
    delta_electrode_fit = numpy.polyfit(temp_points, delta_electrode, 1)

    # define functions
    x = numpy.linspace(30, 130, 130)
    # func_surface = delta_surface_fit[0] * pow(x, 2) + delta_surface_fit[1] * x + delta_surface_fit[2]
    # func_air = delta_air_fit[0] * pow(x, 2) + delta_air_fit[1] * x + delta_air_fit[2]
    # func_electrode = delta_electrode_fit[0] * pow(x, 2) + delta_electrode_fit[1] * x + delta_electrode_fit[2]
    func_surface = delta_surface_fit[0]*x + delta_surface_fit[1]
    func_air = delta_air_fit[0] * x + delta_air_fit[1]
    func_electrode = delta_electrode_fit[0] * x + delta_electrode_fit[1]

    plt.rcParams["font.family"] = "Times New Roman"
    plt.title("Control temperature deviation")
    plt.plot(x, func_surface, "r")
    plt.plot(x, func_air, "b")
    plt.plot(x, func_electrode, "g")
    plt.scatter(temp_points, delta_surface, c='None', edgecolors="red", marker='o', label="Surface")
    plt.scatter(temp_points, delta_air, c='None', edgecolors="blue", marker='^', label="Air")
    plt.scatter(temp_points, delta_electrode, c='None', edgecolors="green", marker='d', label="Electrode")
    plt.xlabel("Control temperature in °C")
    plt.ylabel("Temperature drop in °C")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("temperature_lookup.png", dpi=300)
    plt.show()


# Uncomment the desired action to be executed:

create_lookup_plot()
steady_state_evaluation()
control_temp_delta_evaluation()
