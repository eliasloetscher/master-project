import tkinter as tk
from gui_classes.measurement_frame import MeasurementFrame
from gui_classes.control_frame import ControlFrame
from gui_classes.gui_functions import GUIFunctions
from gui_classes.sub_frame1 import SubFrame1
from gui_classes.sub_frame2 import SubFrame2
from gui_classes.sub_frame3 import SubFrame3

# Initialize Tkinter instance
root = tk.Tk()
root.title("MVISS")
root.option_add("*Font", "TkDefaultFont 12")

# GUI Header
gui_title = tk.Label(root, text="Resistivity Measurement Test Setup", font='Helvetica 18 bold')
gui_title.grid(row=0, columnspan=2, pady=10)

# Initialize main frames
cf = ControlFrame(root)
mf = MeasurementFrame(root)

# Initialize sub frames
sf1 = SubFrame1(cf.control_frame)
sf2 = SubFrame2(cf.control_frame)
sf3 = SubFrame3(cf.control_frame)

# Initialize gui functions object
gui_functions_object = GUIFunctions(sf1.sub_frame1, sf2.sub_frame2, sf3.sub_frame3)

# Set up ControlFrame
cf.set_up(gui_functions_object)

# Execute GUI
root.mainloop()
