"""
Documentation goes here
"""

import time
import tkinter.messagebox
import utilities.measure_module as measure
from parameters import Parameters


def breakdown(hvamp, type, values):
    """

    :param hvamp:
    :return:
    """

    # Set voltage to zero
    hvamp.set_voltage(0)

    # Print to console
    print("--------------------------------------------------------------------")
    print("------------------------ BREAKDOWN DETECTED ------------------------")
    print(" Type: ", type)
    print(" Values: ", values)
    print("--------------------------------------------------------------------")

    # Inform user in GUI
    message = str("Breakdown detected! \n\nType: " + str(type) + "\nValues: " + str(values))
    while not tkinter.messagebox.showerror("BREAKDOWN", message) == "ok":
        time.sleep(1)


def breakdown_detection(root, labjack, electrometer, hvamp, flag):
    """

    :param flag:
    :param hvamp:
    :param electrometer:
    :param labjack:
    :return:
    """

    # Init temporary flag vars
    flag_voltage = False
    flag_current = False

    # --------------- BREAKDOWN DETECTION VIA VOLTAGE --------------- #

    # Measure voltage
    measured_voltage = measure.measure_voltage(hvamp, labjack)

    # Get voltage currently set by user
    user_voltage = hvamp.user_voltage

    # Init values list
    values = [measured_voltage, user_voltage]

    # Calculate allowed absolute deviation from given percentage
    voltage_deviation_abs = user_voltage*Parameters.BD_VOLTAGE_DEVIATION/100

    # Check if voltage deviation is below limit
    if abs(measured_voltage - user_voltage) > voltage_deviation_abs and user_voltage > 0:
        if flag:
            breakdown(hvamp, "Voltage", str("[HVAmp, Setbyuser]" + str(values) + " V"))
        else:
            flag_voltage = True
    else:
        flag_voltage = False

    # --------------- BREAKDOWN DETECTION VIA CURRENT --------------- #

    # Measure current
    measured_current_electrometer = measure.measure_current(electrometer)
    measured_current_hvamp = hvamp.get_current()

    # Get current limit set in 'Parameters'
    current_limit = Parameters.BD_CURRENT_LIMIT

    # Init values list
    values = [measured_current_electrometer, measured_current_hvamp, current_limit]

    # Check if current is below limit
    if measured_current_electrometer > current_limit or measured_current_hvamp > current_limit:
        if flag:
            breakdown(hvamp, "Current", str("[Electrometer, HVAmp, Setbyuser]" + str(values) + " mA"))
        else:
            flag_current = True
    else:
        flag_current = False

    # --------------- FINSIH ROUTINE --------------- #

    # Determine flag
    if flag_voltage or flag_current:
        flag = True

    # Check for breakdown periodically
    root.after(Parameters.BD_INTERVAL*1000, lambda: breakdown_detection(root, labjack, electrometer, hvamp, flag))





