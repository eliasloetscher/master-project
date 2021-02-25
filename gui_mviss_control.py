import tkinter as tk
import tkinter.messagebox

from devices.labjack_t7pro import LabjackConnection
from devices.electrometer_keysight_b2985a import ElectrometerControl
from devices.hv_amp_ultravolt_hva5kv import HVAmp
from devices.sensor_htm2500lf import SensorHtm2500lf
from devices.relays import Relays

from gui_classes.safety_circuit_frame import SafetyCircuitFrame
from gui_classes.control_frame import ControlFrame
from gui_classes.devices_frame import DevicesFrame
from gui_classes.measurement_frame import MeasurementFrame
from gui_classes.recording_frame import RecordingFrame

import utilities.safety_circuit as safety
import utilities.breakdown_detection as bd

from parameters import Parameters


def on_closing(root, electrometer, relays, hvamp):
    """ Method which is called if the user explicitly quits the gui, i.e. clicks on the "X" button on top right corner.

    :param root: tkinter root instance
    :param electrometer: instance of the class Electrometer
    :param relays: instance of the class Relays
    :param hvamp: instance of the class HVAmp
    :return: None
    """

    # ask user for confirmation
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        # switch off all relays
        relays.switch_off_all_relays()
        # set LJ-Tick voltage to zero (hvamp control voltage)
        hvamp.set_voltage(0)
        # set Electrometer voltage to zero, disable ammeter and source
        electrometer.set_voltage(0)
        electrometer.disable_current_input()
        electrometer.disable_source_output()
        # close tkinter instance
        root.destroy()


def gui():
    """ This is the primary gui function for the mviss resistivity measurements test setup.
    All required elements such as devices, utilities, and frames are loaded and initialized.
    Finally, the graphical user interface is started.

    :return: None
    """

    # setup device connections
    labjack = LabjackConnection()
    relays = Relays(labjack)
    electrometer = ElectrometerControl()
    hvamp = HVAmp(labjack)
    humidity_sensor = SensorHtm2500lf(labjack)

    # define basic labjack parameters
    labjack.set_analog_in_resolution(Parameters.LJ_ANALOG_IN_HV_PROBE, 12)  # 12-bit adc resolution

    # define basic electrometer parameters
    electrometer.set_speed('stable')

    # initialize tkinter instance
    root = tk.Tk()

    # start safety circuit
    safety.start_safety_circuit(root, labjack, relays, electrometer, hvamp)

    # start breakdown detection
    #bd.breakdown_detection(root, labjack, relays, electrometer, hvamp, False)

    # set gui name
    root.title("MVISS Control")

    # set global options
    root.option_add("*Font", "TkDefaultFont 12")

    # set and place gui title
    gui_title = tk.Label(root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
    gui_title.grid(row=0, columnspan=2, pady=10)

    # initialize main frames
    DevicesFrame(root, labjack, electrometer)
    SafetyCircuitFrame(root, labjack, relays)
    ControlFrame(root, labjack, relays, electrometer, hvamp)
    MeasurementFrame(root, electrometer, hvamp, humidity_sensor, labjack)
    RecordingFrame(root, electrometer, hvamp, humidity_sensor, labjack, relays)

    # introduce closing action with protocol handler
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, electrometer, relays, hvamp))

    # execute GUI
    root.mainloop()


if __name__ == "__main__":
    # start graphical user interface
    gui()
