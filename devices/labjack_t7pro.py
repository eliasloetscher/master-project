from parameters import Parameters
from labjack import ljm
from labjack.ljm import LJMError


class LabjackConnection:
    """ This class provides a set of methods in order to control the Labjack T7-Pro.
    It is based on the open-source labjack ljm library, officially distributed by labjack ltd.

    Methods
    ---------
    connect()                   Searches the labjack and initializes a connection via USB
    get_handler()               Returns the connection handler
    get_connection_state()      Returns if the connection is alive or not (False/True/None)
    read_analog()               Reads the analog input value from a given port (0-10V)
    read_digital()              Reads the digital input value from a given port (LOW/HIGH)
    write_digital()             Write a digital value (LOW/HIGH) to a given port
    ljtick_dac_set_analog_out() Set the analog output voltage of the DAC LJ-Tick (0-10V)
    set_analog_in_resolution()  Set the bit resolution of a specified analog input port (0-12 bit).

    Note to analog resolution: the higher the resolution, the slower the sampling speed (12 bit -> 159 ms)
    See datasheet for more information.

    Exceptions
    -----------
    TypeError: deviceType or connectionType are not strings.
    LJMError: An error was returned from the LJM library call.
    ConnectionError: The connection setup failed

    """

    def __init__(self):
        """ Constructor of the class LabjackConnection.
         Initialize the class vars and setup a labjack connection handle.
        """

        # labjack connection handle (default: None. If connected: labjack handler instance)
        self.connection_handle = None

        # labjack connection state (default: None, connection_error: False, connected: True)
        self.connection_state = False

        # try to connect
        self.connect()

    def connect(self):
        """ Function used for connecting to labjack with parameters specified in Parameters class.

        :return: True if connection successful, False if connection error occurred
        """

        # check if already connected
        if self.connection_state:
            if Parameters.DEBUG:
                print("Function labjack_connection.connect: already connected!")
            return True
        # if not, try to connect
        else:
            # open Labjack connection with given parameters
            try:
                self.connection_handle = ljm.openS("ANY", Parameters.LABJACK_CONNECTION, Parameters.LABJACK_SERIAL_NUMBER)
            except (ValueError, LJMError):
                if Parameters.DEBUG:
                    print("Couldn't connect to labjack! (part 1)")
                self.connection_state = False
                return False

            # check for success
            if self.connection_handle > 0:
                if Parameters.DEBUG:
                    info = ljm.getHandleInfo(self.connection_handle)
                    print("Function labjack_connection.connect: connection successful!")
                    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
                          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
                          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
                self.connection_state = True
                return True
            # connection not successful
            else:
                if Parameters.DEBUG:
                    print("Couldn't connect to labjack! (part 2)")
                    print("Connection handle is: ", self.connection_handle)
                self.connection_state = False
                return False

    def get_handler(self):
        """ Returns the labjack connection handler

        :return: connection handler instance
        """
        return self.connection_handle

    def get_connection_state(self):
        """ Returns the connection state

        :return: connection state, True if connected, False if not.
        """
        return self.connection_state

    def read_analog(self, port):
        """ Read an analog voltage value from a given port.

        :param port: Analog port to read value from
        :return: Analog input value in Volt [V]
        """

        # try to read
        try:
            result = ljm.eReadName(self.connection_handle, port)
        except (TypeError, LJMError):
            self.connection_state = False
            self.close_connection()
            return False

        return result

    def read_digital(self, port):
        """ Read a digital value and map to "HIGH", or "LOW"

        :param port: Digital port to read value from
        :return: Digital value of a given FIO port, "HIGH", or "LOW" as string
        :exception TypeError: if port is not string
        :exception ValueError: if collected result is not correct
        :exception LJMError: An error was returned from the LJM library call
        """

        # check input parameters
        if not isinstance(port, str):
            raise TypeError

        # try to read digital value from given port
        try:
            result = ljm.eReadName(self.connection_handle, port)
        except (TypeError, LJMError):
            self.connection_state = False
            self.close_connection()
            return False

        # map result to "LOW" or "HIGH"
        if result == 0.0:
            return "LOW"
        elif result == 1.0:
            return "HIGH"
        else:
            raise ValueError

    def write_digital(self, port, value):
        """ Write a digital value ("HIGH" or "LOW") to a given port.

        :param port: Digital port to write a value
        :param value: Value to write, either "HIGH" or "LOW"
        :return: None
        :exception TypeError: if port or value is not string
        :exception ValueError: if value is not "HIGH" or "LOW"
        :exception LJMError: An error was returned from the LJM library call
        """

        # check input parameters
        if not isinstance(value, str) or not isinstance(port, str):
            raise TypeError

        # map input string to write value
        if value == "LOW":
            state = 0
        elif value == "HIGH":
            state = 1
        else:
            raise ValueError

        # try to write
        try:
            ljm.eWriteName(self.connection_handle, port, state)
        except (TypeError, LJMError):
            self.connection_state = False
            self.close_connection()
            return False

    def ljtick_dac_set_analog_out(self, port, voltage):
        """ Writes the analog output voltage to the LJTick DAC 0 to 10 V.

        :param port: "A" or "B", type <str>
        :param voltage: output voltage 0-10V, type <float>
        :return: Labjack I2C acknowledgement (Acked if non-zero value)
        :exception TypeError: if port is not string or voltage is not float
        :exception ValueError: if port is invalid or voltage is out of range
        :exception LJMError: An error was returned from the LJM library call
        """

        # check input parameters
        if not isinstance(port, str) or not isinstance(voltage, float):
            raise TypeError

        if voltage < -10 or voltage > 10:
            raise ValueError

        # Generate write statement. Even TDAC# is DACA, odd TDAC# is DACB
        # Labjack doc: For instance, if LJTick-DAC is connected to FIO6/FIO7 block on main device:
        # TDAC6 corresponds with DACA, and TDAC7 corresponds with DACB.
        if port == "A":
            write = str("TDAC" + str(Parameters.LJ_TICK_DAC_DOUT_SCL))
        elif port == "B":
            write = str("TDAC" + str(Parameters.LJ_TICK_DAC_DOUT_SDA))
        else:
            raise ValueError

        # try to write value
        try:
            ljm.eWriteName(self.connection_handle, write, voltage)
        except (TypeError, LJMError):
            self.connection_state = False
            self.close_connection()
            return False

    def set_analog_in_resolution(self, port, resolution):
        """ Set the measurement resolution of an analog input port.

        :param port: AIN0 - AIN12
        :param resolution: adc resolution in bits (0-12)
        :exception TypeError: if port is not string or voltage is not float
        :exception ValueError: if port is invalid or voltage is out of range
        :exception LJMError: An error was returned from the LJM library call
        :return: None
        """

        # check input parameters
        if not isinstance(port, str) or not isinstance(resolution, int):
            raise TypeError

        if not port[0:3] == "AIN":
            raise ValueError

        # get port number from given port
        if len(port) == 4:
            port_number = int(port[3])
        elif len(port) == 5:
            port_number = int(port[3:5])
        else:
            raise ValueError

        # check if port number is valid
        if port_number < 0 or port_number > 12:
            raise ValueError

        # check if given resolution is valid
        if resolution < 0 or resolution > 12:
            raise ValueError

        # prepare write statement
        write = str(port + "_RESOLUTION_INDEX")

        # try to write
        try:
            ljm.eWriteName(self.connection_handle, write, resolution)
        except (TypeError, LJMError):
            self.connection_state = False
            self.close_connection()
            return False

    def close_connection(self):
        """ Closes the labjack connection.

        :return: None
        """
        try:
            ljm.close(self.connection_handle)
        except LJMError:
            pass
