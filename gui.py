import tkinter as tk

from gui_classes.safety_circuit_frame import SafetyCircuitFrame
from gui_classes.control_frame import ControlFrame
from gui_classes.devices_frame import DevicesFrame
from gui_classes.measurement_frame import MeasurementFrame
from gui_classes.recording_frame import RecordingFrame

from gui_classes.gui_functions import GUIFunctions

from gui_classes.sub_frame1 import SubFrame1
from gui_classes.sub_frame2 import SubFrame2
from gui_classes.sub_frame3 import SubFrame3

from mviss_module.labjack_connection import LabjackConnection
from mviss_module.gpio_functions import GPIOFunctions
from sensors.htm2500lf import Htm2500lf
from mviss_module.parameters import Parameters
from devices.hvamp import HVAmp
from keysight.electrometer_control import ElectrometerControl
import sys
from labjack.ljm import LJMError


# function for safety circuit
def check_safety_circuit(connection, lj_gpio):
    state_s1 = connection.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
    state_s2 = connection.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
    state_safety_relay = lj_gpio.get_safety_relay_state()

    # if Parameters.DEBUG:
        # print("State S1: ", state_s1)
        # print("State S2: ", state_s2)
        # print("State safety relay: ", state_safety_relay)

    # Note: if state is HIGH, switch is closed!
    if state_s1 == "HIGH" and state_s2 == "HIGH" and state_safety_relay == "ON":
        connection.write_digital(Parameters.LJ_DIGITAL_OUT_SIGNAL_LAMP, "LOW")
    else:
        connection.write_digital(Parameters.LJ_DIGITAL_OUT_SIGNAL_LAMP, "HIGH")

    root.after(1000, lambda: check_safety_circuit(connection, lj_gpio))


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

# Setup electrometer
electrometer = ElectrometerControl()

# Initialize Tkinter instance
root = tk.Tk()
root.title("MVISS")
root.option_add("*Font", "TkDefaultFont 12")

# start safety circuit
root.after(0, lambda: check_safety_circuit(lj_connection, lj_gpio))

# GUI Header
gui_title = tk.Label(root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
gui_title.grid(row=0, columnspan=2, pady=10)

# Initialize gui_functions_instance
gui_functions = GUIFunctions()

# Initialize main frames
devices_frame = DevicesFrame(root, gui_functions, lj_connection, electrometer)
safety_circuit_frame = SafetyCircuitFrame(root, gui_functions)
control_frame = ControlFrame(root, gui_functions)

measurment_frame = MeasurementFrame(root, gui_functions)
recording_frame = RecordingFrame(root, gui_functions)

# start label autoupdate
devices_frame.auto_update_labels(root, lj_connection, electrometer)

"""
# Initialize sub frames
sf1 = SubFrame1(control_frame.control_frame, lj_connection, lj_gpio, hvamp)
sf2 = SubFrame2(control_frame.control_frame, electrometer)
sf3 = SubFrame3(control_frame.control_frame)

# Initialize gui functions object
# gui_functions_object = GUIFunctions(sf1.sub_frame1, sf2.sub_frame2, sf3.sub_frame3)

# Set up ControlFrame
# control_frame.set_up(gui_functions)

# start plot
# sf2.start_plotting(root, gui_functions, electrometer)

# Show sensor values
# sensor_frame.show_measurements(gui_functions_object, humidity_sensor, hvamp)

# Setup plots

# Start plot frame
sf2.show_measurements(gui_functions, humidity_sensor, electrometer, hvamp)

"""

# Execute GUI
root.mainloop()
