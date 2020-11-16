from mviss_module.parameters import Parameters
import mviss_module.measure_module as measure
from labjack.ljm import LJMError


class GUIFunctions:

    def __init__(self):
        # self.sub_frame1 = sub_frame1
        # self.sub_frame2 = sub_frame2
        # self.sub_frame3 = sub_frame3
        self.debug = Parameters.DEBUG

        self.datapoints = []

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

    def update_measurement_section(self, measurement_frame, humidity_sensor, hvamp):
        # Get all sensor values
        values = measure.measure_all_values(humidity_sensor, hvamp)

        # Update all gui labels
        measurement_frame.volt1.set(round(float(values[0]), 2))
        measurement_frame.current1.set(round(float(values[1]), 2))
        measurement_frame.temp1.set(round(float(values[2]), 2))
        measurement_frame.temp2.set(round(float(values[3]), 2))
        measurement_frame.humidity1.set(round(values[4], 2))

        if self.debug:
            print("All gui measurement labels updated with function update_measurement_section")

    def update_current_plot(self, plot_frame, electrometer, ax, graph):

        if len(self.datapoints) >= 50:
            # delete first element from list
            self.datapoints = self.datapoints[1:len(self.datapoints)]

        # Get electrometer value
        value = measure.measure_current(electrometer)

        # Add to datapoints list
        self.datapoints.append(value)

        if Parameters.DEBUG:
            print(self.datapoints)
            print(len(self.datapoints))

        ax.cla()
        ax.grid()
        ax.plot(range(len(self.datapoints)), self.datapoints, marker='o', color='orange')
        graph.draw()

        if self.debug:
            print("Plot updated")

    def start_auto_update_current_plot(self, root_instance, plot_frame, electrometer, hvamp):
        self.update_current_plot(plot_frame, electrometer, hvamp)
        root_instance.after(500, lambda: self.start_auto_update_current_plot(root_instance, plot_frame, electrometer, hvamp))

