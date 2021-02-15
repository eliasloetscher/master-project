import numpy
import matplotlib.pyplot as plt

x_20 = [0,13.25,25.31,37.68,50.46,62.41,73.96,81.31,84.08]
x_25 = [0,9.70,20.74,29.44,40.79,50.48,60.94,71.18,82.10]
x_30 = [0, 10]

y_20 = [0,9.89,20.01,30.14,40.38,50.33,61.20,66.58,67.04]
y_25 = [0,6.19,14.64,21.64,29.17,37.19,44.55,52.99,60.72]
y_30 = [0, 10]

result_20 = numpy.polyfit(x_20, y_20, 1)
result_25 = numpy.polyfit(x_25, y_25, 1)
result_30 = numpy.polyfit(x_30, y_30, 1)

x = numpy.linspace(0, 100, 10)
func_20 = result_20[0]*x + result_20[1]
func_25 = result_25[0]*x + result_25[1]
func_30 = result_30[0]*x + result_30[1]

plt.rcParams["font.family"] = "Times New Roman"
plt.plot(x_20, y_20, "b")
plt.plot(x_25, y_25, "r")
plt.plot(x_30, y_30, "g")
plt.scatter(x_20, y_20, c='None', edgecolors="blue", marker='o', label="RH @ T=20°C")
plt.scatter(x_25, y_25, c='None', edgecolors="red", marker='^', label="RH @ T=25°C")
plt.scatter(x_30, y_30, c='None', edgecolors="green", marker='d', label="RH @ T=30°C")
plt.title("Humidity Look-Up Table")
plt.xlabel("RH inside mixing chamber in %")
plt.ylabel("RH inside test cell in %")
plt.legend(loc="lower right")
plt.grid()
# y_ticks = [0, 5, 10, 15, 20, 25, 30]
# plt.yticks(y_ticks)
# plt.savefig("pos_volt_shift_electrometer.png", dpi=300)
plt.show()
plt.cla()

