from devices.sensor_htm2500lf import HumiditySensorHtm2500lf
from devices.labjack_t7pro import LabjackConnection
import utilities.log_module as log
import time
import numpy


def test_series(test_temp):
    lj_connection = LabjackConnection()
    log.create_logfile(str("humidity_validation_"+test_temp))
    log.log_message("date, time, absolute_time_in_ms, t_mix_chamber, t_test_cell, hum_mix_chamber, hum_test_cell")

    while True:

        # get sensor values
        test_cell_humidity_in_mv = lj_connection.read_analog("AIN13")*1000
        test_cell_temp_in_mv = lj_connection.read_analog("AIN12")*1000
        mix_chamber_humidity_in_mv = lj_connection.read_analog("AIN0")*1000
        mix_chamber_temp_in_mv = lj_connection.read_analog("AIN10")*1000

        # convert humidity values
        test_cell_humiduty_converted = round(0.0375 * test_cell_humidity_in_mv - 37.7, 2)
        mix_chamber_humidity_converted = round(0.0375 * mix_chamber_humidity_in_mv - 37.7, 2)

        # convert test cell temperature
        tcr = (10000*test_cell_temp_in_mv)/(5000-test_cell_temp_in_mv)
        test_cell_temp_in_k = 1/(8.54942*pow(10, -4) + 2.57305*pow(10, -4)*numpy.log(tcr) + 1.65368*pow(10, -7)*pow(numpy.log(tcr), 3))
        test_cell_temp_in_deg_c = round(test_cell_temp_in_k - 273.15, 2)

        # convert mix chamber temperature
        mcr = (10000*mix_chamber_temp_in_mv)/(5000-mix_chamber_temp_in_mv)
        mix_chamber_temp_in_k = 1/(8.54942*pow(10, -4) + 2.57305*pow(10, -4)*numpy.log(mcr) + 1.65368*pow(10, -7)*pow(numpy.log(mcr), 3))
        mix_chamber_temp_in_deg_c = round(mix_chamber_temp_in_k - 273.15, 2)

        # print(mix_chamber_temp_in_deg_c, test_cell_temp_in_deg_c, mix_chamber_humidity_converted, test_cell_humiduty_converted)

        # log values
        values = [mix_chamber_temp_in_deg_c, test_cell_temp_in_deg_c, mix_chamber_humidity_converted, test_cell_humiduty_converted]
        log.log_values(values)
        time.sleep(1)


test_series("hum_test_valuesaadsfsafs")