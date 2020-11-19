from devices.labjack_t7pro import LabjackConnection
import time

handle = LabjackConnection()
# print(handle.connection_state)

while True:
    print(handle.check_connection())
    time.sleep(1)