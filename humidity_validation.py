from devices.humidity_sensor_htm2500lf import Htm2500lf
from devices.labjack_t7pro import LabjackConnection
import utilities.log_module as log
import time


def validation_mixing_chamber(wait_time_humid_air, wait_time_dry_air, repetitions, measure_interval):
    lj_connection = LabjackConnection()
    hum_sensor = Htm2500lf(lj_connection)
    log.create_logfile("humidity_validation")

    for i in range(0, repetitions + 1):
        input("Set air flow to 100% humidity. Press Enter to continue ...")
        log.log_message("Starting to measure humidity, setting: 100 % humid air")
        time_now = time.time()
        end_time = time_now + wait_time_humid_air
        while time.time() < end_time:
            log.log_values([hum_sensor.read_humidity()])
            time.sleep(measure_interval)
        log.log_message("Finished measurement \n \n")

        input("Set air flow to 100% dry air. Press Enter to continue ...")
        log.log_message("Starting to measure humidity, setting: 100 % dry air")
        time_now = time.time()
        end_time = time_now + wait_time_dry_air
        while time.time() < end_time:
            log.log_values([hum_sensor.read_humidity()])
            time.sleep(measure_interval)
        log.log_message("Finished measurement \n \n")

        time.sleep(1)


validation_mixing_chamber(600, 600, 2, 2)
