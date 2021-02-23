import numpy
import matplotlib.pyplot as plt

x_20 = [0,9.12,20.64,30.87,40.82,50.65,60.12,70.41,80.31]
x_25 = [0,9.70,20.74,29.44,40.79,50.48,60.94,71.18,82.10]
x_30 = [0,9.98,19.87,30.82,40.54,50.31,60.20,71.69,80.95]

y_20 = [0,8.82,19.29,29.19,38.62,47.68,56.99,66.50,76.06]
y_25 = [0,6.44,15.08,22.56,30.70,38.87,46.57,55.43,63.61]
y_30 = [0,4.74,11.05,18.19,24.59,31.01,38.36,44.64,49.42]

result_20 = numpy.polyfit(x_20, y_20, 1)
result_25 = numpy.polyfit(x_25, y_25, 1)
result_30 = numpy.polyfit(x_30, y_30, 1)

x = numpy.linspace(0, 85, 10)
func_20 = result_20[0]*x + result_20[1]
func_25 = result_25[0]*x + result_25[1]
func_30 = result_30[0]*x + result_30[1]

plt.rcParams["font.family"] = "Times New Roman"
plt.plot(x, func_20, "b")
plt.plot(x, func_25, "r")
plt.plot(x, func_30, "g")
plt.scatter(x_20, y_20, c='None', edgecolors="blue", marker='o', label="RH @ T=20°C")
plt.scatter(x_25, y_25, c='None', edgecolors="red", marker='^', label="RH @ T=25°C")
plt.scatter(x_30, y_30, c='None', edgecolors="green", marker='d', label="RH @ T=30°C")
plt.title("Humidity look-up table")
plt.xlabel("RH in mixing chamber in % (T=20°C)")
plt.ylabel("RH in test cell in %")
plt.legend(loc="lower right")
plt.grid()

plt.savefig("humidity_lookup_table.png", dpi=300)
plt.show()
plt.cla()

