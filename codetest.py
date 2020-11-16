from mviss_module.labjack_connection import LabjackConnection
import time

handle = LabjackConnection()
# print(handle.connection_state)

while True:
    print(handle.check_connection())
    time.sleep(1)