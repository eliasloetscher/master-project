import tkinter as tk
import tkinter.messagebox

from devices.labjack_t7pro import LabjackConnection
from devices.electrometer_keysight_b2985a import ElectrometerControl
from devices.hv_amp_ultravolt_hva5kv import HVAmp
from devices.humidity_sensor_htm2500lf import HumiditySensorHtm2500lf
from devices.relays import Relays

from gui_classes.safety_circuit_frame import SafetyCircuitFrame
from gui_classes.control_frame import ControlFrame
from gui_classes.devices_frame import DevicesFrame
from gui_classes.measurement_frame import MeasurementFrame
from gui_classes.recording_frame import RecordingFrame

import utilities.safety_circuit as safety


def on_closing(root, relays):
    """ Method which is called if the user explicitly quits the gui, i.e. clicks on the "X" button on top right corner

    :param root: tkinter root instance
    :param relays: object for controlling the relays (use the corresponding class in the package 'devices'
    :return: None
    """

    # Ask user for confirmation
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        # Switch off all relays
        relays.switch_off_all_relays()
        # Close tkinter instance
        root.destroy()


def gui():
    """ This is the primary gui function for the mviss resistivity measurements test setup.
    All required elements such as devices, utilities, and frames are loaded and initialized.
    Finally, the graphical user interface is started.

    :return: None
    """

    # Setup device connections
    labjack = LabjackConnection()
    relays = Relays(labjack)
    electrometer = ElectrometerControl()
    hvamp = HVAmp(labjack)
    humidity_sensor = HumiditySensorHtm2500lf(labjack)

    # Initialize tkinter instance
    root = tk.Tk()

    # Start safety circuit
    safety.start_safety_circuit(root, labjack, relays)

    # Set gui name
    root.title("MVISS")

    # Set global options
    root.option_add("*Font", "TkDefaultFont 12")

    # Set and place gui title
    gui_title = tk.Label(root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
    gui_title.grid(row=0, columnspan=2, pady=10)

    # Initialize main frames
    DevicesFrame(root, labjack, electrometer)
    SafetyCircuitFrame(root, labjack, relays)
    ControlFrame(root, labjack, relays, electrometer, hvamp)
    MeasurementFrame(root, electrometer, hvamp, humidity_sensor)
    RecordingFrame(root, electrometer, hvamp, humidity_sensor)

    # Introduce closing action with protocol handler
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, relays))

    # Execute GUI
    root.mainloop()


if __name__ == "__main__":
    # Start graphical user interface
    gui()
