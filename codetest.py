import numpy
import matplotlib.pyplot as plt
import math

x = [20, 30, 40, 50, 60, 70, 80]
y = []
data = [2.12, 3.38, 5.25, 6.92, 8.49, 9.52, 9.43]

func = numpy.polyfit(x, data, 5)
print(func)
for i in range(100):
    y.append(pow((func[0]*i), 4)+ pow((func[1]*i), 3)+ pow((func[2]*i), 2)+func[3]*i + func[4])

print(y)


print(len(x))
print(len(y))
plt.xlim(0, 99)
plt.plot(y)
plt.show()


