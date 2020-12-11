# Main python script

from devices.labjack_t7pro import LabjackConnection
from devices.sensor_htm2500lf import Htm2500lf
from devices.hv_amp_ultravolt_hva5kv import HVAmp

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

hva = HVAmp(connection)
hva.set_voltage(1000)

"""
i = 0.0
while True:
    connection.ljtick_dac_set_analog_out("B", i)
    i += 1
    time.sleep(3)
"""
