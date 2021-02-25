"""
This module provides several logging functions for simplifying the recording process
"""

import time
import datetime
from parameters import Parameters
from pathlib import Path
import utilities.measure_module as measure

# init global vars
LOCATION = Parameters.LOCATION_LOG_FILES
filename = ""  # Leave empty. filename is generated automatically at runtime.

# debug mode
debug = Parameters.DEBUG


def create_logfile(name):
    """ Creates a valid filename according to given parameters. Writes header. Saved at global var LOCATION.

    :param name: file name given by usser input
    :return: None
    """

    # generate filename
    global filename
    filename = str(name) + ".txt"
    path = Path(LOCATION + filename)
    if debug:
        print("Filename:", filename)
        print("Location:", path)

    # check if file already exists. If so, increase number until filename does not exist
    i = 1
    while path.exists():
        filename = str(name) + "_Num_" + str(i) + ".txt"
        path = Path(LOCATION + filename)
        i += 1
        if debug:
            print("Filename:", filename)
            print("Location:", path)

    # prepare header information
    dt_now = datetime.datetime.now()

    # write header information to file
    with open(str(LOCATION + filename), 'a') as logfile:
        logfile.write("HEADER INFORMATION" + "\n")
        logfile.write("Date: " + dt_now.strftime("%d-%m-%Y") + "\n")
        logfile.write("Time: " + dt_now.strftime("%H:%M:%S") + "\n \n")
        logfile.write("TEST INFORMATION" + "\n")
        logfile.write("Original filename given by user input: " + str(name) + "\n \n")
        logfile.write("DATA \n")


def log_all_values(electrometer, hvamp, humidity_sensor):
    """ This method gets and records all sensor values to the file specified in the global var 'filename'.

    :param electrometer: instance of the electrometer connection
    :param hvamp: instance of the hvamp connection
    :param humidity_sensor:  instance of the humidity sensor
    :return: None
    """

    # write variable name line
    log_message("date, time, absolute_time, voltage, current, temperature, hum_sensor_humidity, hum_sensor_temp, "
                "measurement_range")

    # get all sensor values
    values = measure.measure_all_values(electrometer, hvamp, humidity_sensor)

    # log all sensor values
    log_values(values)


def log_values(value_list):
    """ This method logs all values given in the value_list. Location: global var LOCATION.
        Function create_logfile must being called once in order to run this function.

    :param value_list: values to log
    :return: None
    """

    # check input parameters
    if not isinstance(value_list, list):
        raise TypeError
    if len(value_list) == 0:
        raise ValueError

    # check if global filename exists
    global filename
    if filename == "":
        if debug:
            print("No logfile is set up. Call function create_logfile() first!")
        raise ValueError
    # try to write all sensor values
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
    # catch all exceptions (not according to PEP8 but highest robustness) which is needed for recording measurements
    except:
        if debug:
            print("An error occured during logging")
        pass


def log_message(msg):
    """ This method logs the given message at a preset location (global var LOCATION).
     Function create_logfile must being called once in order to run this function.

     :param msg: Content which has to be logged
     :return: False if error occurred (no logfile), True if log was successful
    """

    # check if file exists
    global filename
    if filename == "":
        if debug:
            print("No logfile is set up. Call function create_logfile() first!")
        return False

    # write message to file
    try:
        with open(str(LOCATION + filename), 'a') as logfile:
            # Log parameter msg
            logfile.write(str(msg + "\n"))
    # catch all exceptions (not according to PEP8 but highest robustness) which is needed for recording measurements
    except:
        if debug:
            print("An error occured during logging")
        return False

    return True


def finish_logging():
    """ Finishes the recording process by resetting the global filename variable

    :return: None
    """
    # reset global variable 'filename'
    global filename
    filename = ""
