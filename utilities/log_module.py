# This module provides several logging functions.

import time
import datetime
from parameters import Parameters
from pathlib import Path
import utilities.measure_module as measure


# Global vars
LOCATION = Parameters.LOCATION_LOG_FILES
filename = ""  # Leave empty. filename is generated automatically at runtime.

# Debug mode
debug = Parameters.DEBUG


def create_logfile(name):
    """
    Creates a valid filename according to given parameters. Writes header. Saved at global var LOCATION
    :param name: user input file name
    :return: None
    """
    # generate filename
    global filename
    filename = str(name) + ".txt"
    path = Path(LOCATION + filename)
    if debug:
        print("Filename:", filename)
        print("Location:", path)

    # Check if file already exists. If so, increase number until filename does not exist
    i = 1
    while path.exists():
        filename = str(name) + "_Num_" + str(i) + ".txt"
        path = Path(LOCATION + filename)
        i += 1
        if debug:
            print("Filename:", filename)
            print("Location:", path)

    # Prepare header information
    dt_now = datetime.datetime.now()

    with open(str(LOCATION + filename), 'a') as logfile:
        logfile.write("HEADER INFORMATION" + "\n")
        logfile.write("Date: " + dt_now.strftime("%d-%m-%Y") + "\n")
        logfile.write("Time: " + dt_now.strftime("%H:%M:%S") + "\n \n")
        logfile.write("TEST INFORMATION" + "\n")
        logfile.write("Original filename given by user input: " + str(name) + "\n \n")
        logfile.write("DATA \n")


def log_all_values(electrometer, hvamp, humidity_sensor):

    # write variable name line
    log_message("date, time, absolute_time, voltage, current, temperature, humidity")

    # Get all sensor values
    values = measure.measure_all_values(electrometer, hvamp, humidity_sensor)

    # Log all sensor values
    log_values(values)


def log_values(value_list):
    """
        This function logs all values given in the value_list.
        Location: global var LOCATION.
        Function create_logfile must being called once in order to run this function.
    :param value_list: values to log
    """

    if not isinstance(value_list, list):
        raise TypeError

    if len(value_list) == 0:
        raise ValueError

    global filename
    if filename == "":
        if debug:
            print("No logfile is set up. Call function create_logfile() first!")
        raise ValueError

    try:
        with open(str(LOCATION + filename), 'a') as logfile:
            # Log date and time
            dt_now = datetime.datetime.now()
            logfile.write(str(dt_now.strftime("%d-%m-%Y") + ","))
            logfile.write(str(dt_now.strftime("%H:%M:%S") + ","))
            logfile.write(str(str(int(round(time.time() * 1000))) + ","))

            # Log all values comma separated
            if debug:
                print("Value list for logging: ", value_list)
            for i in range(len(value_list) - 1):
                logfile.write(str(value_list[i]) + ',')
            logfile.write(str(value_list[len(value_list) - 1]) + "\n")
    except:
        if debug:
            print("An error occured during logging")
        pass


def log_message(msg):
    """
     This function logs the given message at a preset location (global var LOCATION).
     Function create_logfile must being called once in order to run this function.

     :param msg: Content which has to be logged
     :return: 0 if error occurred (no logfile), 1 if log was successful
    """

    global filename
    if filename == "":
        if debug:
            print("No logfile is set up. Call function create_logfile() first!")
        return 0

    try:
        with open(str(LOCATION + filename), 'a') as logfile:
            # Log parameter msg
            logfile.write(str(msg + "\n"))
    except:
        if debug:
            print("An error occured during logging")
        return 0

    return 1


def finish_logging():
    global filename
    filename = ""
