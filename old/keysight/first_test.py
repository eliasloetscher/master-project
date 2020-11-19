from devices.electrometer_keysight_b2985a import ElectrometerControl
import time

inst = ElectrometerControl()
print("Set voltage to 0 V")
inst.set_voltage(0)
time.sleep(3)
print("Set voltage to 50 V")
inst.set_voltage(50)
inst.enable_source_output()

while True:
    print(round(float(inst.get_current())*1000*1000*1000*1000, 5), " pA")
    time.sleep(0.1)

"""
print("type ", type(inst.get_interlock_state()))
print("Voltage in V:", round(float(inst.get_voltage()), 2))
print("Current in pA:", round(float(inst.get_current())*1000*1000*1000*1000, 5))
print("Temperature in °C:", round(float(inst.get_temperature()), 2))
inst.close_connection()
"""
