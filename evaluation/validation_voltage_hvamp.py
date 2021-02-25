import numpy
import matplotlib.pyplot as plt

# init x data
x_pos_points = [10, 50, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
x_neg_points = [0, -10, -50, -100, -250, -500, -750, -1000, -1500, -2000, -2500, -3000, -3500, -4000, -4500, -5000]

# init y data
y_pos_points = [1.70233, 1.3316, 1.8831, 3.8386, 7.41717, 10.6748, 13.5113, 21.5909, 29.8405, 38.9045,
                49.3759, 60.0450, 72.4371, 85.5864, 98.2680]
y_neg_points = [-1.9513, -1.4333, -1.9281, -1.4482, 0.7215, 2.5356, 4.6853, 7.7570, 15.7873, 25.2621, 33.5024,
                44.0791, 55.5167, 66.6903, 80.1431, 93.2848]

# fit data with a polynomial of degree 2
result_pos = numpy.polyfit(x_pos_points, y_pos_points, 2)
result_neg = numpy.polyfit(x_neg_points, y_neg_points, 2)

# print coefficients
print("Positive voltage correction polynom: ", result_pos)
print("Negative voltage correction polynom: ", result_neg)

# create plot for positive voltages
plt.rcParams["font.family"] = "Times New Roman"
x = numpy.linspace(0, 5000, 100)
func = result_pos[0]*pow(x, 2) + result_pos[1] * x + result_pos[2]
print(func)
plt.plot(x, func, label="fit function")
plt.scatter(x_pos_points, y_pos_points, color="red", label="data points")
plt.title("Positive Voltage Shift")
plt.xlabel("Set Voltage in V")
plt.ylabel("Voltage drop in V")
plt.legend(loc="lower right")
plt.grid()
plt.savefig("pos_volt_shift_hvamp.png", dpi=300)
plt.show()
plt.cla()

# create plot for negative voltages
plt.rcParams["font.family"] = "Times New Roman"
x = numpy.linspace(0, -5000, 100)
y_ticks = [0, 20, 40, 60, 80, 100]
print(y_ticks)
func = result_neg[0] * pow(x, 2) + result_neg[1] * x + result_neg[2]
plt.plot(x, func, label="fit function")
plt.scatter(x_neg_points, y_neg_points, color="red", label="data points")
plt.title("Negative Voltage Shift")
plt.xlabel("Set Voltage in V")
plt.ylabel("Voltage drop in V")
plt.yticks(y_ticks)
plt.grid()
plt.savefig("neg_volt_shift_hvamp.png", dpi=300)
plt.show()
