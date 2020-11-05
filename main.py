# Main python script

import time
from mviss_module.labjack_connection import LabjackConnection
from sensors.htm2500lf import Htm2500lf

connection = LabjackConnection()
hum_sensor = Htm2500lf(connection)

"""
while True:
    connection.write_digital("FIO0", "LOW")
    print("FIO0: ", connection.read_digital("FIO0"))
    time.sleep(3)
    connection.write_digital("FIO0", "HIGH")
    print("FIO0: ", connection.read_digital("FIO0"))
    time.sleep(3)
"""

"""
while True:
    humidity = hum_sensor.read_humidity()
    print("Humidity: ", humidity)
    time.sleep(2)
"""

connection.ljtick_dac_set_analog_out("A", 0.0)
connection.ljtick_dac_set_analog_out("B", 0.0)

"""
i = 0.0
while True:
    connection.ljtick_dac_set_analog_out("B", i)
    i += 1
    time.sleep(3)
"""
