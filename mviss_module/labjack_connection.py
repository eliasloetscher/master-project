from mviss_module.parameters import Parameters
from labjack import ljm
from labjack.ljm import LJMError


class LabjackConnection:

    def __init__(self):
        """
        Raises:
        TypeError: deviceType or connectionType are not strings.
        LJMError: An error was returned from the LJM library call.
        ConnectionError: The connection setup failed
        """

        # Open Labjack connection with given parameters
        try:
            self.connection = ljm.openS("ANY", Parameters.LABJACK_CONNECTION, Parameters.LABJACK_SERIAL_NUMBER)
        except (ValueError, LJMError):
            pass

        # Check for success
        print(self.connection)
        if self.connection == 1:
            if Parameters.DEBUG:
                info = ljm.getHandleInfo(self.connection)
                print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
                      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
                      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
        else:
            raise ConnectionError

    def get_handler(self):
        """

        :return: connection handler
        """
        return self.connection

    def read_analog(self, port):
        """

        :param port: Analog port to read value from
        :return: Analog input value in Volt [V]
        """
        return ljm.eReadName(self.connection, port)

    def read_digital(self, port):
        """

        :param port: Digital port to read value from
        :return: Digital value of a given FIO port
        :exception TypeError: if port is not string
        :exception ValueError: if collected result is not correct
        :exception LJMError: An error was returned from the LJM library call
        """
        if not isinstance(port, str):
            raise TypeError

        result = -1
        try:
            result = ljm.eReadName(self.connection, port)
        except (TypeError, LJMError):
            pass

        if result == 0.0:
            return "LOW"
        elif result == 1.0:
            return "HIGH"
        else:
            raise ValueError

    def write_digital(self, port, value):
        """

        :param port: Digital port to write a value
        :param value: Value to write, either "HIGH" or "LOW"
        :return: None
        :exception TypeError: if port or value is not string
        :exception ValueError: if value is not "HIGH" or "LOW"
        :exception LJMError: An error was returned from the LJM library call
        """

        if not isinstance(value, str) or not isinstance(port, str):
            raise TypeError

        if value == "LOW":
            state = 0
        elif value == "HIGH":
            state = 1
        else:
            raise ValueError

        try:
            ljm.eWriteName(self.connection, port, state)
        except (TypeError, LJMError):
            pass

    def ljtick_dac_set_analog_out(self, port, voltage):
        """
        Writes the analog output voltage to the LJTick DAC 0 to 10 V.
        :param port: "A" or "B", type <str>
        :param voltage: output voltage 0-10V, type <float>
        :return: Labjack I2C acknowledgement (Acked if non-zero value)
        :exception TypeError: if port is not string or voltage is not float
        :exception ValueError: if port is invalid or voltage is out of range
        :exception LJMError: An error was returned from the LJM library call
        """

        if not isinstance(port, str) or not isinstance(voltage, float):
            raise TypeError

        if voltage < 0 or voltage > 10:
            raise ValueError

        # Generate write statement. Even TDAC# is DACA, odd TDAC# is DACB
        # Labjack doc: For instance, if LJTick-DAC is connected to FIO2/FIO3 block on main device:
        # TDAC2 corresponds with DACA, and TDAC3 corresponds with DACB.
        if port == "A":
            write = str("TDAC" + str(Parameters.LJ_TICK_DAC_DOUT_SCL))
        elif port == "B":
            write = str("TDAC" + str(Parameters.LJ_TICK_DAC_DOUT_SDA))
        else:
            raise ValueError

        try:
            ljm.eWriteName(self.connection, write, voltage)
        except (TypeError, LJMError):
            pass

    def close_connection(self):
        """
        Closes the labjack connection
        :return:
        """
        ljm.close(self.connection)
