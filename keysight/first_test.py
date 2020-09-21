from keysight.electrometer_control import ElectrometerControl

inst = ElectrometerControl()
inst.get_idn_response()
inst.set_voltage(21)
print("Interlock state: ", inst.get_interlock_state())
print("type ", type(inst.get_interlock_state()))
print("Voltage in V:", round(float(inst.get_voltage()), 2))
print("Current in pA:", round(float(inst.get_current())*1000*1000*1000*1000, 5))
print("Temperature in °C:", round(float(inst.get_temperature()), 2))
inst.close_connection()
