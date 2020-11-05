from mviss_module.parameters import Parameters


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
