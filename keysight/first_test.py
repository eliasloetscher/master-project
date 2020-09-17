from keysight.electrometer_control import ElectrometerControl

inst = ElectrometerControl()
inst.get_idn_response()
inst.close_connection()