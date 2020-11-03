from mviss_module.parameters import Parameters
import mviss_module.measure_module as measure
from labjack.ljm import LJMError


class GUIFunctions:

    def __init__(self, sub_frame1, sub_frame2, sub_frame3):
        self.sub_frame1 = sub_frame1
        self.sub_frame2 = sub_frame2
        self.sub_frame3 = sub_frame3
        self.debug = Parameters.DEBUG

    def show_sub_frame1(self):
        self.sub_frame1.grid(row=4, padx=10, columnspan=4, sticky="W")
        self.sub_frame2.grid_forget()
        self.sub_frame3.grid_forget()

    def show_sub_frame2(self):
        self.sub_frame1.grid_forget()
        self.sub_frame2.grid(row=4, padx=10, columnspan=4, sticky="W")
        self.sub_frame3.grid_forget()

    def show_sub_frame3(self):
        self.sub_frame1.grid_forget()
        self.sub_frame2.grid_forget()
        self.sub_frame3.grid(row=4, padx=10, columnspan=4, sticky="W")

    def update_measurement_section(self, measurement_frame, humidity_sensor):
        # Get all sensor values
        values = measure.measure_all_values(humidity_sensor)

        # Update all gui labels
        measurement_frame.volt1.set(round(float(values[0]), 2))
        measurement_frame.current1.set(round(float(values[1]), 2))
        measurement_frame.temp1.set(round(float(values[2]), 2))
        measurement_frame.temp2.set(round(float(values[3]), 2))
        measurement_frame.humidity1.set(round(values[4], 2))

        if self.debug:
            print("All gui measurement labels updated with function update_measurement_section")