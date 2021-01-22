"""
Documentation goes here
"""

import time
import tkinter.messagebox
import utilities.measure_module as measure
from parameters import Parameters


def breakdown(hvamp, labjack, electrometer, relays, type, values):
    """

    :param hvamp:
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
    message = str("Breakdown detected! \n\nType: " + str(type) + "\nValues: " + str(values))
    while not tkinter.messagebox.showerror("BREAKDOWN", message) == "ok":
        time.sleep(1)


def breakdown_detection(root, labjack, relays, electrometer, hvamp, flag):
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
        if abs(measured_voltage - user_voltage) > voltage_deviation_abs and user_voltage > 0:
            if flag:
                breakdown(hvamp, labjack, electrometer, relays, "Voltage", str("[Measured, Setbyuser]" + str(values) + " V"))
            else:
                flag_voltage = True
        else:
            flag_voltage = False

    # --------------- BREAKDOWN DETECTION VIA CURRENT --------------- #

    # Measure current
    measured_current_electrometer_in_pa = 0
    # measured_current_electrometer_in_pa = measure.measure_current(electrometer)
    measured_current_hvamp = hvamp.get_current()

    # convert to mA
    measured_current_electrometer_in_ma = measured_current_electrometer_in_pa*0.001*0.001

    # Get current limit set in 'Parameters'
    current_limit = Parameters.BD_CURRENT_LIMIT

    # Init values list
    values = [measured_current_electrometer_in_ma, measured_current_hvamp, current_limit]

    # Check if current is below limit
    if measured_current_electrometer_in_ma > current_limit or measured_current_hvamp > current_limit:
        if flag:
            breakdown(hvamp, labjack, electrometer, relays, "Current", str("[Electrometer, HVAmp, Setbyuser]" + str(values) + " mA"))
        else:
            flag_current = True
    else:
        flag_current = False

    # --------------- FINSIH ROUTINE --------------- #

    # Determine flag
    if flag_voltage or flag_current:
        flag = True

    # Check for breakdown periodically
    root.after(Parameters.BD_INTERVAL*1000, lambda: breakdown_detection(root, relays, labjack, electrometer, hvamp, flag))





