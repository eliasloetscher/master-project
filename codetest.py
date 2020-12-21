import numpy
import matplotlib.pyplot as plt
import time
from labjack import ljm
from devices.labjack_t7pro import LabjackConnection

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
