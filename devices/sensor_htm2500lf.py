from parameters import Parameters
import numpy


class SensorHtm2500lf:
    """ This class provides a set of methods to control the humidity and temperature sensor Htm2500lf.

    Methods
    ---------
    read_humidity()     Get and return relative humidity in %
    read_temperature()  Get and return temperature in °C

    """

    def __init__(self, labjack_connection):
        """ Constructor of the class Sensor Htm2500lf

        :param labjack_connection: Requires an instance of the class LabjackConnection for reading LJ ports

        """

        # init class var for labjack connection
        self.lj_connection = labjack_connection

    def read_humidity(self):
        """ Read the humidity and convert to the relative humidity according to formula from datasheet.

        :return: Relative humidity in %
        """

        # read analog IN at humidity sensor port
        result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HUMIDITY_SENSOR)

        # convert from V to RH in % with linear equation according to datasheet
        convert = 0.0375*result*1000 - 37.7

        # block negative humidity and return zero instead
        if convert < 0:
            convert = 0

        return convert

    def read_temperature(self):
        """ Read the temperature and convert to degree celsius according to formula from datasheet.

        :return: Temperature in °C
        """

        # read analog input at temp sensor port
        result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_TEMP_SENSOR) * 1000

        # convert from mV to degree celsius with steinhart equations according to datasheet
        resistance = (10000 * result) / (5000 - result)
        test_cell_temp_in_k = 1 / (8.54942 * pow(10, -4) + 2.57305 * pow(10, -4) * numpy.log(resistance) + 1.65368 * pow(10, -7) * pow(numpy.log(resistance), 3))
        test_cell_temp_in_deg_c = round(test_cell_temp_in_k - 273.15, 2)

        return test_cell_temp_in_deg_c
