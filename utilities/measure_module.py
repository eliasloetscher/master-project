from parameters import Parameters


def measure_all_values(electrometer, hvamp, humidity_sensor):
    """

    :return: All sensor values
    """

    hv_amp_voltage = round(measure_voltage(hvamp), 2)
    electrometer_current = round(measure_current(electrometer), 2)
    electrometer_temperature = round(measure_temperature(electrometer), 2)
    humidity = round(measure_humidity(humidity_sensor), 2)

    values = [hv_amp_voltage, electrometer_current, electrometer_temperature, humidity]

    if Parameters.DEBUG:
        print("measured values: ", values)

    return values


def measure_voltage(hvamp):
    return hvamp.get_voltage()


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


def measure_humidity(hum_sensor):
    return hum_sensor.read_humidity()
