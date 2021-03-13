import csv
import statistics
import numpy
import matplotlib.pyplot as plt

# import data from log files
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


def read_csv(file):
    """ This method extracts the data from the log files and returns each row in a list

    :param file: logfile for data extraction
    :return: each row of the logfile separted in a list
    """

    # init lists for storing the extracted data
    time = []
    time_absolute = []
    temp_row_one = []
    temp_row_two = []
    temp_row_three = []

    # extract data
    with open(file) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar=',')
        i = 0
        for row in spamreader:
            i += 1
            if i < 4:
                continue
            time.append(row[0])
            time_absolute.append(row[1])
            temp_row_one.append(row[2])
            temp_row_two.append(row[3])
            temp_row_three.append(row[4])

    # return data
    return [time, time_absolute, temp_row_one, temp_row_two, temp_row_three]


def steady_state(temp, dev):
    """ Determines the time when a steady-state is reached based on an allowed deviation

    :param temp: temperature data list
    :param dev: deviation allowed for determining the steady-state
    :return: None
    """

    # one hour in time steps (6 measurements per minute)
    timedelta = 6 * 60

    # startindex
    index = 3

    # search steady state time
    while len(temp) > index + timedelta:

        # init three elements for each time range
        elements_one = [temp[index], temp[index+1], temp[index+2]]
        elements_two = [temp[index+timedelta], temp[index+1+timedelta], temp[index+2+timedelta]]

        # convert elements of first time range to float
        elements_one_float = []
        for element in elements_one:
            elements_one_float.append(float(element[1:len(element) - 1]))

        # convert elements of second time range to float
        elements_two_float = []
        for element in elements_two:
            elements_two_float.append(float(element[1:len(element) - 1]))

        # calculate mean values for each time range
        element_one_float = statistics.mean(elements_one_float)
        element_two_float = statistics.mean(elements_two_float)

        # compare the element of the second time range to the one of the first time range.
        # If difference is smaller than the given deviation, the steady state is reached.
        if abs(element_two_float - element_one_float) < dev:
            steady_state_time = (index-2)*10/60/60
            return steady_state_time

        # increase time step by one, moving forward in the data list
        index += 1

    return "not found"


def calculate_delta(temp_list, dev, control_temp):
    """ Calculates the temperature drop at steady-state time between the T_set and T_is for a given temperature list.

    :param temp_list: temperature data list
    :param dev: allowed deviation for defining the steady-state
    :param control_temp: the control temperature set at the temperature control unit, i.e. T_set
    :return: temperature drop in degree celsius
    """

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
    """ Evaluate the time until stead-state is reached for every temperature investigated.

    :return: None
    """

    # Set titles for print section
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
    """ Evaluate the temperatue drop at steady-state for each investigated temperature.

    :return: None
    """

    # init titles for print section
    titles = ["30 °C", "55 °C", "80 °C", "105 °C", "130 °C"]

    # init control temperatures, i.e. T-set
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
    """ Create lookup plot for master thesis based on 5 investigated temperatures

    :return: None
    """

    # init data based on function of this module
    temp_points = [30, 55, 80, 105, 130]
    delta_surface = [2.04, 4.04, 7.01, 11.01, 14.64]
    delta_air = [2.89, 6.37, 12.16, 15.41, 18.52]
    delta_electrode = [3.08, 7.24, 13.28, 15.75, 20.80]

    # calculate coefficients for interpolation
    delta_surface_fit = numpy.polyfit(temp_points, delta_surface, 1)
    delta_air_fit = numpy.polyfit(temp_points, delta_air, 1)
    delta_electrode_fit = numpy.polyfit(temp_points, delta_electrode, 1)

    # define functions based on polynomial fit
    x = numpy.linspace(30, 130, 130)
    func_surface = delta_surface_fit[0]*x + delta_surface_fit[1]
    func_air = delta_air_fit[0] * x + delta_air_fit[1]
    func_electrode = delta_electrode_fit[0] * x + delta_electrode_fit[1]

    # create plot
    plt.rcParams["font.family"] = "Times New Roman"
    # plt.title("Control temperature deviation")
    plt.plot(x, func_surface, "r")
    plt.plot(x, func_air, "b")
    plt.plot(x, func_electrode, "g")
    plt.scatter(temp_points, delta_surface, c='None', edgecolors="red", marker='o', label="Inner surface of test cell")
    plt.scatter(temp_points, delta_air, c='None', edgecolors="blue", marker='^', label="Air at medium height")
    plt.scatter(temp_points, delta_electrode, c='None', edgecolors="green", marker='d', label="Between the electrodes")
    plt.xlabel("Control temperature in °C")
    plt.ylabel("Temperature drop in °C")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("temperature_lookup.png", dpi=300)
    plt.show()


def plot(x_list, y_list, save_name):

    # create plot
    plt.rcParams["font.family"] = "Times New Roman"
    # plt.title("Control temperature deviation")
    plt.plot(x_list, y_list[1], "r", mfc='None', marker='o', markevery=500, label="Inner surface of test cell")
    plt.plot(x_list, y_list[0], "b", mfc='None', marker='^', markevery=500, label="Air at medium height")
    plt.plot(x_list, y_list[2], "g", mfc='None', marker='d', markevery=500, label="Between the electrodes")
    plt.xlabel("Time in h")
    plt.ylabel("Temperature in °C")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig(save_name, dpi=300)
    plt.show()


def plot_every_measurement():

    safe_names = ["temp_30", "temp_55", "temp_80", "temp_105", "temp_130"]
    for i in range(5):

        # get csv results
        result = read_csv(FILE_LOCATIONS[i])

        # match to temps
        sensors = SENSORS[i]
        temp_surface = result[sensors[0] + 1]
        temp_air = result[sensors[1] + 1]
        temp_electrode = result[sensors[2] + 1]

        total_time_in_h = len(temp_surface)*10/3600
        x_points = []
        for m in range(len(temp_air)):
            time_point_in_hours = round(total_time_in_h/len(temp_air)*m,3)
            if time_point_in_hours < 15:
                x_points.append(time_point_in_hours)

        temp_surface = temp_surface[0:len(x_points)]
        temp_air = temp_air[0:len(x_points)]
        temp_electrode = temp_electrode[0:len(x_points)]

        surface_float = []
        for element in temp_surface:
            if i == 3:
                surface_float.append(float(element[2:len(element) - 2]))
                continue
            surface_float.append(float(element[1:len(element) - 1]))

        air_float = []
        for element in temp_air:
            if i == 3:
                air_float.append(float(element[2:len(element) - 2]))
                continue
            air_float.append(float(element[1:len(element) - 1]))

        electrode_float = []
        for element in temp_electrode:
            if i == 3:
                electrode_float.append(float(element[2:len(element) - 2]))
                continue
            electrode_float.append(float(element[1:len(element) - 1]))

        print(x_points)
        print(temp_air)

        plot(x_points, [air_float, surface_float, electrode_float], safe_names[i])


# Uncomment the desired action to be executed:

create_lookup_plot()
# steady_state_evaluation()
# control_temp_delta_evaluation()
# plot_every_measurement()
