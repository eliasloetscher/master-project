import numpy
import matplotlib.pyplot as plt

x_pos_points = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

x_neg_points = [0, -100, -200, -300, -400, -500, -600, -700, -800, -900, -1000]

y_pos_points = [1.78, 4.06, 6.52, 8.98, 11.46, 13.93, 16.29, 18.73, 21.11, 23.48, 25.85]

y_neg_points = [-1.78, 0.87, 3.35, 5.81, 8.27, 10.71, 13.12, 15.53, 17.88, 20.28, 22.61]

result_pos = numpy.polyfit(x_pos_points, y_pos_points, 2)
result_neg = numpy.polyfit(x_neg_points, y_neg_points, 2)

print("Positive voltage correction polynom: ", result_pos)
print("Negative voltage correction polynom: ", result_neg)

plt.rcParams["font.family"] = "Times New Roman"
x = numpy.linspace(0, 1000, 100)
func = result_pos[0]*pow(x, 2) + result_pos[1] * x + result_pos[2]
print(func)
plt.plot(x, func, label="fit function")
plt.scatter(x_pos_points, y_pos_points, color="red", label="data points")
plt.title("Positive Voltage Shift")
plt.xlabel("Set Voltage in V")
plt.ylabel("Voltage drop in V")
plt.legend(loc="lower right")
plt.grid()
y_ticks = [0, 5, 10, 15, 20, 25, 30]
plt.yticks(y_ticks)
plt.savefig("pos_volt_shift_electrometer.png", dpi=300)
plt.show()
plt.cla()

plt.rcParams["font.family"] = "Times New Roman"
x = numpy.linspace(0, -1000, 100)
y_ticks = [0, 5, 10, 15, 20, 25, 30]
print(y_ticks)
func = result_neg[0] * pow(x, 2) + result_neg[1] * x + result_neg[2]
plt.plot(x, func, label="fit function")
plt.scatter(x_neg_points, y_neg_points, color="red", label="data points")
plt.title("Negative Voltage Shift")
plt.xlabel("Set Voltage in V")
plt.ylabel("Voltage drop in V")
plt.yticks(y_ticks)
plt.grid()
plt.savefig("neg_volt_shift_electrometer.png", dpi=300)
plt.show()

