from parameters import Parameters


def measure_all_values(humidity_sensor, hvamp):
    """

    :return: All sensor values
    """

    humidity = humidity_sensor.read_humidity()
    hv_amp_voltage = hvamp.get_voltage()
    hv_amp_current = hvamp.get_current()

    values = [hv_amp_voltage, hv_amp_current, 0, 0, humidity]

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


