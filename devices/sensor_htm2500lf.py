from parameters import Parameters
import numpy


class SensorHtm2500lf:

    def __init__(self, labjack_connection):
        """

        :param labjack_connection: Requires an instance of the class LabjackConnection for reading LJ ports
        """
        self.lj_connection = labjack_connection

    def read_humidity(self):
        """

        :return:
        """
        # Read analog IN at humidity sensor port
        result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HUMIDITY_SENSOR)

        # Convert from V to RH in % with linear equation according to datasheet
        convert = 0.0375*result*1000 - 37.7

        return convert

    def read_temperature(self):
        """

        :return:
        """

        # Read analog IN at temp sensor port
        result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_TEMP_SENSOR) * 1000

        # Convert from mV to degree celsios with steinhart equations according to datasheet
        resistance = (10000 * result) / (5000 - result)
        test_cell_temp_in_k = 1 / (8.54942 * pow(10, -4) + 2.57305 * pow(10, -4) * numpy.log(resistance) + 1.65368 * pow(10, -7) * pow(numpy.log(resistance), 3))
        test_cell_temp_in_deg_c = round(test_cell_temp_in_k - 273.15, 2)

        return test_cell_temp_in_deg_c