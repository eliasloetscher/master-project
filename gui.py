import tkinter as tk
from gui_classes.sensor_frame import SensorFrame
from gui_classes.control_frame import ControlFrame
from gui_classes.gui_functions import GUIFunctions
from gui_classes.sub_frame1 import SubFrame1
from gui_classes.sub_frame2 import SubFrame2
from gui_classes.sub_frame3 import SubFrame3
from mviss_module.labjack_connection import LabjackConnection
from mviss_module.gpio_functions import GPIOFunctions
from sensors.htm2500lf import Htm2500lf
from mviss_module.parameters import Parameters
from devices.hvamp import HVAmp
import sys
from labjack.ljm import LJMError

# Setup labjack connection
lj_connection = LabjackConnection()

# Switch off all relays
try:
    # Note: Relays are low-active. 'HIGH' corresponds to 'OFF' (!)
    lj_connection.write_digital(Parameters.LJ_DIGITAL_OUT_SAFETY_RELAY, "HIGH")
    lj_connection.write_digital(Parameters.LJ_DIGITAL_OUT_GND_RELAY, "HIGH")
    lj_connection.write_digital(Parameters.LJ_DIGITAL_OUT_HV_RELAY, "HIGH")
except (ValueError, TypeError, LJMError):
    if Parameters.DEBUG:
        print("CRITICAL ERROR. ASSURE ALL RELAYS ARE SWITCHED OFF")
    sys.exit()

# Setup labjack gpio object
lj_gpio = GPIOFunctions()

# Setup humidity sensor
humidity_sensor = Htm2500lf(lj_connection)

# Setup high voltage amplifier
hvamp = HVAmp(lj_connection)

# Initialize Tkinter instance
root = tk.Tk()
root.title("MVISS")
root.option_add("*Font", "TkDefaultFont 12")

# GUI Header
gui_title = tk.Label(root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
gui_title.grid(row=0, columnspan=2, pady=10)

# Initialize main frames
control_frame = ControlFrame(root)
sensor_frame = SensorFrame(root)

# Initialize sub frames
sf1 = SubFrame1(control_frame.control_frame, lj_connection, lj_gpio, hvamp)
sf2 = SubFrame2(control_frame.control_frame)
sf3 = SubFrame3(control_frame.control_frame)

# Initialize gui functions object
gui_functions_object = GUIFunctions(sf1.sub_frame1, sf2.sub_frame2, sf3.sub_frame3)

# Set up ControlFrame
control_frame.set_up(gui_functions_object)

# Show sensor values
sensor_frame.show_measurements(gui_functions_object, humidity_sensor, hvamp)

# Execute GUI
root.mainloop()
