"""
This module implements the breakdown detection based on two mechanisms:
- If the current is above a specified limit (default 100 nA)
- If the voltage deviates more than a specified percentage (default 10%)
"""

import time
import tkinter.messagebox
import utilities.measure_module as measure
from parameters import Parameters


def breakdown(hvamp, labjack, electrometer, relays, type, values):
    """ This method is executed if a breakdown is detected. Both voltage sources are immediately switched off,
    the HV relay is opened, the GND relay is closed, and the user is informed via popup message.

    :param hvamp: instance of the hvamp connection
    :param labjack: instance of the labjack connection
    :param electrometer: instance of the electrometer connection
    :param relays: instance of the class relays
    :param type: type of the breakdwon detection mechanism, either 'current' or 'voltage'
    :param values: sensor values collected during breakdown
    :return:
    """

    # Set voltages to zero
    hvamp.set_voltage(0)
    electrometer.set_voltage(0)

    # open HV relay, close GND relay for safety
    relays.switch_relay("HV", "OFF", labjack)
    relays.switch_relay("GND", "ON", labjack)

    # Print to console
    print("--------------------------------------------------------------------")
    print("------------------------ BREAKDOWN DETECTED ------------------------")
    print(" Type: ", type)
    print(" Values: ", values)
    print("--------------------------------------------------------------------")

    # Inform user in GUI
    if type == 'Voltage':
        message = str("Voltage deviation! \n\nValues: " + str(values)+"\n\nPossible reasons: \n-Wrong source connected"
                                                                      "\n-Both relays closed\n-Breakdown occurred")
    elif type == 'Current':
        message = str("Current limit exceeded! \n\nValues: " + str(values)+"\n\n Please check setup!")
    else:
        raise ValueError

    while not tkinter.messagebox.showerror("ERROR", message) == "ok":
        time.sleep(1)


def breakdown_detection(root, labjack, relays, electrometer, hvamp, flag):
    """ Measures the voltage and current at an interval specified in the module parameters. Triggers the
    breakdown method if a breakdown is detected according to the mechanisms described in the introduction of this file.

    :param root: gui root instance for displaying the popup
    :param labjack: instance of the labjack connection
    :param relays: instance of the class relays
    :param electrometer: instance of the elctrometer connection
    :param hvamp: instance of the high voltage amplifier class
    :param flag: is either True or False, used for detection of two deviating datapoints in a row
    :return:
    """

    # init temporary flag vars
    flag_voltage = False
    flag_current = False

    # --------------- BREAKDOWN DETECTION VIA VOLTAGE --------------- #

    # measure voltage
    measured_voltage = measure.measure_voltage(labjack)

    # get voltage currently set by user
    user_voltage_hvamp = hvamp.user_voltage
    user_voltage_electrometer = electrometer.user_voltage
    if user_voltage_hvamp > 0:
        user_voltage = user_voltage_hvamp
    elif user_voltage_electrometer > 0:
        user_voltage = user_voltage_electrometer
    else:
        user_voltage = 0

    # init values list
    values = [measured_voltage, user_voltage]

    # calculate allowed absolute deviation from given percentage
    voltage_deviation_abs = user_voltage*Parameters.BD_VOLTAGE_DEVIATION/100

    # check if hv relay is closed -> otherwise hv probe will measure zero volt
    if relays.hv_relay_state == 'closed':
        # check if voltage deviation is below limit
        if abs(measured_voltage - user_voltage) > voltage_deviation_abs and user_voltage > 10:
            if flag:
                breakdown(hvamp, labjack, electrometer, relays, "Voltage", str("[Measured, Setbyuser]" + str(values) + " V"))
            else:
                flag_voltage = True
        else:
            flag_voltage = False

    # --------------- BREAKDOWN DETECTION VIA CURRENT --------------- #

    # measure current
    measured_current_electrometer_in_pa = measure.measure_current(electrometer)
    measured_current_hvamp = hvamp.get_current()

    # convert to mA
    measured_current_electrometer_in_ma = measured_current_electrometer_in_pa*0.001*0.001

    # get current limit set in 'Parameters'
    current_limit = Parameters.BD_CURRENT_LIMIT

    # init values list
    values = [measured_current_electrometer_in_ma, measured_current_hvamp, current_limit]

    # check if current is below limit
    if measured_current_electrometer_in_ma > current_limit or measured_current_hvamp > current_limit:
        if flag:
            breakdown(hvamp, labjack, electrometer, relays, "Current", str("[Electrometer, HVAmp, Setbyuser]" + str(values) + " mA"))
        else:
            flag_current = True
    else:
        flag_current = False

    # --------------- FINSIH ROUTINE --------------- #

    # determine flag
    if flag_voltage or flag_current:
        flag = True

    # check for breakdown periodically
    root.after(Parameters.BD_INTERVAL*1000, lambda: breakdown_detection(root, labjack, relays, electrometer, hvamp, flag))
