from mviss_module.parameters import Parameters
from labjack import ljm


class Htm2500lf:

    def __init__(self, labjack_connection):
        """

        :param labjack_connection: Requires an instance of the class LabjackConnection for reading LJ ports
        """
        self.lj_connection = labjack_connection

    def read_humidity(self):
        """

        :return:
        """
        # Read analog IN where the sensor is connected
        result = self.lj_connection.read_analog(Parameters.LJ_ANALOG_IN_HUMIDITY_SENSOR)

        # Convert from V to RH in % with linear equation according to datasheet
        convert = 0.0375*result*1000 - 37.7

        return convert
