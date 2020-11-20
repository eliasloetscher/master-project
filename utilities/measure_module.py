from parameters import Parameters


def measure_all_values(electrometer, hvamp, humidity_sensor):
    """

    :return: All sensor values
    """

    humidity = humidity_sensor.read_humidity()
    hv_amp_voltage = hvamp.get_voltage()
    electrometer_current = electrometer.get_current()
    electrometer_temperature = electrometer.get_temperature()

    values = [hv_amp_voltage, electrometer_current, electrometer_temperature, humidity]

    if Parameters.DEBUG:
        print("measured values: ", values)

    return values


def measure_current(electrometer):
    result = electrometer.get_current()
    result_in_picoampere = round(float(result)*1000*1000*1000*1000, 5)
    if Parameters.DEBUG:
        print(result_in_picoampere)
    return result_in_picoampere


def measure_temperature(electrometer):
    result = electrometer.get_temperature()
    result_in_celsius = round(float(result), 2)
    if Parameters.DEBUG:
        print(result_in_celsius)
    return result_in_celsius


