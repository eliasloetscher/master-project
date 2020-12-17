import numpy
import matplotlib.pyplot as plt
import time
from labjack import ljm
from devices.labjack_t7pro import LabjackConnection

labjack = LabjackConnection()
handler = labjack.get_handler()
print(ljm.eReadName(handler, "AIN0_RESOLUTION_INDEX"))
for i in range(5):
    print(labjack.read_analog("AIN0"))
    time.sleep(1)

print("RES 12")
ljm.eWriteName(handler, "AIN0_RESOLUTION_INDEX", 12)
print(ljm.eReadName(handler, "AIN0_RESOLUTION_INDEX"))

for i in range(5):
    print(labjack.read_analog("AIN0"))
    time.sleep(1)

ljm.eWriteName(handler, "AIN0_RESOLUTION_INDEX", 5)
print(ljm.eReadName(handler, "AIN0_RESOLUTION_INDEX"))

print("RES 5")
for i in range(5):
    print(labjack.read_analog("AIN0"))
    time.sleep(1)


