
def measure_all_values(humidity_sensor):
    """

    :return: All sensor values
    """

    humidity = humidity_sensor.read_humidity()

    return [0, 0, 0, 0, humidity]
