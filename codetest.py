import numpy
import matplotlib.pyplot as plt
import time
import tkinter as tk
from labjack import ljm
from devices.labjack_t7pro import LabjackConnection
from devices.electrometer_keysight_b2985a import ElectrometerControl
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from gui_classes.auto_run_frame import AutoRunFrame

data_time = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
data_points = [0, 1, 0, 3, 0, 0, 6, 7, 8, 0]

for i in range(0, len(data_time)):
    index_mirrored = len(data_time) - i - 1
    if data_points[index_mirrored] == 0:
        del (data_points[index_mirrored])
        del (data_time[index_mirrored])

print(data_time)
print(data_points)

"""

class App:
    def __init__(self, master):
        # VARIABLES
        self.inputFile = ""
        self.fig = plt.Figure()

        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master = master)
        self.canvas.get_tk_widget().pack()

        self.axes = self.fig.add_subplot(111)
        x_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.line, = self.axes.plot(x_array, y_array)
        NavigationToolbar2Tk(self.canvas, root)

        self.canvas.draw()

        subplots[i].plot(range(len(self.overview_data[i])), self.overview_data[i])

        # FRAME
        frame = tk.Frame(master)
        master.title("MassyTools 0.1.1 (Alpha)")


root = tk.Tk()
app = App(root)
root.mainloop()





#instance = ElectrometerControl()
"""
"""
instance.set_speed('quick')
i = 0
while True:
    print(instance.get_current())
    time.sleep(1)
    i += 1
    if i == 5:
        break

instance.set_speed('normal')
i=0
print("normal")
while True:
    print(instance.get_current())
    time.sleep(1)
    i += 1
    if i == 5:
        break
"""


"""
x_points = [0, 10, 50, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
y_points = [-1.84866666666667, 1.70233333333333, 1.33166666666667, 1.88311475409836, 3.83868852459022,
            7.41711864406767, 10.674833333333, 13.5113333333334, 21.5909836065575,
            29.8405084745759, 38.9045000000001, 49.3759999999997, 60.0450819672137,
            72.4371666666661, 85.5864406779665, 98.2680327868857]

result = numpy.polyfit(x_points, y_points, 2)

print(result)

x = numpy.linspace(0, 50, 100)
func = result[0] * pow(x, 2) + result[1] * x + result[2]
# func = result[0]*pow(x, 5) + result[1]*pow(x, 4) + result[2]*pow(x, 3) + result[3]*pow(x, 2) + result[4]*x + result[5]
plt.plot(x, func)
plt.scatter(x_points, y_points, color="red")

plt.show()

"""
