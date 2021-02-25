"""
This module provides measurement methods for all sensor included in the mviss test setup.
The idea of a centralized handling is that the measurement is always done the same way including conversion.
-> Always use these methods (instead of directly accessing the class instances of the devices)
"""

from parameters import Parameters


def measure_all_values(electrometer, hvamp, humidity_sensor, labjack):
    """ This method returns the four key measurements of the mviss test setup:
    [voltage in V, current in pA, temperature in °C, relative humidity in %]

    :param electrometer: instance of the class Electrometer
    :param hvamp: instance of the class HVAmp
    :param humidity_sensor: instance of the clas HumiditySensor
    :param labjack: instance of the class Labjack
    :return: [voltage in V, current in pA, temperature in °C, relative humidity in %]
    """

    # get all sensor values using the methods in this module and round to two digits
    hv_amp_voltage = round(measure_voltage(labjack), 2)
    electrometer_current = round(measure_current(electrometer), 2)
    electrometer_temperature = round(measure_temperature(electrometer), 2)
    humidity = round(measure_humidity(humidity_sensor), 2)

    # prepare for return
    values = [hv_amp_voltage, electrometer_current, electrometer_temperature, humidity]

    # print values if debug mode is on
    if Parameters.DEBUG:
        print("measured values: ", values)

    return values


def measure_voltage(labjack):
    """ This method returns the voltage in V measured with the high voltage probe including voltage correction
    according to the method described in the master thesis (or separate documentation)

    :param labjack: instance of the labjack class
    :return: voltage in V
    """

    # get analog value
    analog_read = labjack.read_analog("AIN0")

    # map (0-5V to 0-5000V)
    voltage = 1000 * analog_read

    # execute voltage correction for high voltage amplifier according to polynomial fit (see master thesis or doc)
    if Parameters.active_source == 'h':
        # correct with function
        if voltage > 3:
            coefficients = [1.63206300e-06, 1.14120940e-02, 5.85082426e-01]
            correction = coefficients[0]*pow(voltage, 2) + coefficients[1]*voltage + coefficients[2]
        elif voltage < 3:
            coefficients = [1.95647789e-06, -9.47588563e-03, -2.37081434e+00]
            correction = -(coefficients[0]*pow(voltage, 2) + coefficients[1]*voltage + coefficients[2])
        else:
            correction = 1.66

    # execute voltage correction for electrometer according to polynomial fit (see master thesis or doc)
    elif Parameters.active_source == 'e':
        if voltage > 3:
            coefficients = [-3.78787879e-07,  2.45724242e-02,  1.68181818e+00]
            correction = coefficients[0] * pow(voltage, 2) + coefficients[1] * voltage + coefficients[2]
        elif voltage < 3:
            coefficients = [-1.11072261e-06, -2.54261772e-02, -1.71979021e+00]
            correction = -(coefficients[0] * pow(voltage, 2) + coefficients[1] * voltage + coefficients[2])
        else:
            correction = 1.59
    else:
        print("ERROR: Active source value is wrong!")
        raise ValueError

    # correct voltage
    real_voltage = voltage + correction

    return real_voltage


def measure_current(electrometer):
    """ This method returns the current in pA measured by the electrometer.

    :param electrometer: instance of the class Electrometer
    :return: current in pA
    """

    # get current and convert to pA
    result = electrometer.get_current()
    result_in_picoampere = round(float(result)*1000*1000*1000*1000, 5)

    # check for overflow (current larger than measure range max limit, in this case 1E50 pA is 'measured')
    if abs(result_in_picoampere) > pow(10, 20):
        print("OVERFLOW OCCURRED!")
        return 0

    return result_in_picoampere


def measure_temperature(electrometer):
    """ This method returns the temperature in °C from the K-type sensor via electrometer.

    :param electrometer: instance of the class Electrometer
    :return: temperature in °C
    """

    # get temperature and round to two digits
    result = electrometer.get_temperature()
    result_in_celsius = round(float(result), 2)

    return result_in_celsius


def measure_humidity(hum_sensor):
    """ This method returns the relative humidity in % measured with the humidity sensor Htm2500lf

    :param hum_sensor: instance of humidity sensor Htm2500lf
    :return: relative humidity in %
    """
    return hum_sensor.read_humidity()
