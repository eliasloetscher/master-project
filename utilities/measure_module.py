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
    coefficients = [1.73204040e-06, 1.08167280e-02, 1.27723794e+00]
    correction = coefficients[0]*pow(voltage, 2) + coefficients[1]*voltage + coefficients[2]
    if voltage < 0:
        correction = 1.66

    real_voltage = voltage + correction

    return real_voltage


def measure_current(electrometer):
    result = electrometer.get_current()
    result_in_picoampere = round(float(result)*1000*1000*1000*1000, 5)
    return result_in_picoampere


def measure_temperature(electrometer):
    result = electrometer.get_temperature()
    result_in_celsius = round(float(result), 2)
    if Parameters.DEBUG:
        print(result_in_celsius)
    return result_in_celsius


def measure_humidity(hum_sensor):
    return hum_sensor.read_humidity()
