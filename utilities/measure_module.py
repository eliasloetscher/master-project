from parameters import Parameters


def measure_all_values(electrometer, hvamp, humidity_sensor, labjack):
    """

    :return: All sensor values
    """

    hv_amp_voltage = round(measure_voltage(hvamp, labjack), 2)
    electrometer_current = round(measure_current(electrometer), 2)
    electrometer_temperature = round(measure_temperature(electrometer), 2)
    humidity = round(measure_humidity(humidity_sensor), 2)

    values = [hv_amp_voltage, electrometer_current, electrometer_temperature, humidity]

    if Parameters.DEBUG:
        print("measured values: ", values)

    return values


def measure_voltage(hvamp, labjack):

    # Get analog value
    analog_read = labjack.read_analog("AIN0")

    # map (0-5V to 0-5000V)
    voltage = 1000 * analog_read

    # correct with function
    if voltage > 3:
        coefficients = [1.63206300e-06, 1.14120940e-02, 5.85082426e-01]
        correction = coefficients[0]*pow(voltage, 2) + coefficients[1]*voltage + coefficients[2]

    elif voltage < 3:
        coefficients = [1.95647789e-06, -9.47588563e-03, -2.37081434e+00]
        correction = -(coefficients[0]*pow(voltage, 2) + coefficients[1]*voltage + coefficients[2])
    else:
        correction = 1.66

    real_voltage = voltage + correction

    return real_voltage


def measure_current(electrometer):
    result = electrometer.get_current()
    result_in_picoampere = round(float(result)*1000*1000*1000*1000, 5)

    # check for overflow (current larger than measure range max limit, in this case 1E50 pA is 'measured')
    if abs(result_in_picoampere) > pow(10, 20):
        print("OVERFLOW OCCURRED!")
        return 0
    return result_in_picoampere


def measure_temperature(electrometer):
    result = electrometer.get_temperature()
    result_in_celsius = round(float(result), 2)
    if Parameters.DEBUG:
        print(result_in_celsius)
    return result_in_celsius


def measure_humidity(hum_sensor):
    return hum_sensor.read_humidity()
