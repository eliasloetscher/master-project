import pyvisa as visa
from parameters import Parameters
from pyvisa import VisaIOError
import time


class InterlockError(Exception):
    """ Exception raised when an action is not possible due to open or closed interlock
        Example: Trying to set voltage >26 V when interlock is open
    """
    pass


class ElectrometerControl:
    """ This class provides a set of methods in order to control the electrometer Keysight B2985a via USB.
    The communication is based on scpi and the valid keywords are specified in the 'scpi reference guide'.

    Methods
    ---------
    connect()               Open a connection and initialize session and resource manager
    check_connection()      Check if connection is alive and if not, try to reconnect
    get_idn_response()      Returns the electrometer idn response (system information and identification)
    get_voltage()           Reads the voltage of the internal voltage source in V
    set_voltage()           Set the voltage of the internal voltage source in V
    get_current()           Reads the current in A
    get_temperature()       Reads the temperature in °C
    get_interlock_state()   Reads the current state of the interlock (True/False)
    enable_source_output()  Enables the source output (internal relay)
    disable_source_output() Disables the source output
    enable_current_input()  Enables the amperemeter (internal relay)
    disable_current_input() Disables the amperemeter (i.e. internally connected to gnd)
    close_connection()      Closes the usb connection and resets the state variables

    """

    def __init__(self):
        """ Constructor of the class ElectrometerControl

        Initializes the class variables for
            - session
            - connection state
            - resource manager
            - amperemeter state
        """

        # Electrometer session (default: None. If connected: electrometer session instance)
        self.session = None

        # Electrometer connection state (default: None, connection_error: False, connected: True)
        self.connection_state = False

        # Electrometer resource manager
        self.rm = None

        # State of the ampere meter: enabled (True) or disabled (False)
        self.ampmeter_state = False

        # measurement range variable (0 corresponds to 'auto')
        self.range = 0
        self.range_mode = 'auto'

        # Try to connect
        self.connect()

    def connect(self):
        """ Function used for connecting to Keysight electrometer with address specified in Parameters class

        :return: True if connection successful, False if connection error occurred
        """

        # Check if already connected
        if self.connection_state:
            if Parameters.DEBUG:
                print("Function electrometer_control.connect: already connected!")
            return True

        # Setup a connection
        try:
            # Create a connection (session) to the instrument
            self.rm = visa.ResourceManager()
            self.session = self.rm.open_resource(Parameters.KEYSIGHT_VISA_ADDRESS)
        except visa.Error:
            if Parameters.DEBUG:
                print("Couldn't connect to electrometer!")
            self.connection_state = False
            return False
        else:
            if Parameters.DEBUG:
                print("Successful! Created visa session.")
                print(self.get_idn_response())
            self.connection_state = True
            return True

    def check_connection(self):
        """ This method checks if the connection is still alive and if not, a reconnection attempt is made

        :return: False if connection is not alive, True otherwise
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            return False

        # Try to ask if the usb connection is enabled. If an error occurs, the connection is down
        try:
            self.session.write('SYST:COMM:ENAB? USB')
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return True

    def get_idn_response(self):
        """ Returns the electrometer idn response (system information)

        :return: idn response as String
        """

        # Try to read IDN response
        try:
            self.session.write('*IDN?')
            idn = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        # Print idn response
        if Parameters.DEBUG:
            print('*IDN? returned: %s' % idn.rstrip('\n'))

        return idn

    def get_voltage(self):
        """ Reads the voltage of the internal voltage source in V

        :return: False if connection is not alive, voltage in V otherwise
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to read voltage
        try:
            self.session.write('MEAS:VOLT:DC?')
            voltage = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return voltage

    def set_voltage(self, voltage):
        """
        Sets the voltage of the internal voltage source immediately.

        :param voltage: Voltage to set
        :exception ValueError: If voltage is out of range (<0 V or > 1000 V)
        :exception InterlockError: If Voltage is > 21 V and interlock is open
        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Check input parameter. Maximum output voltage is 1000 V.
        if voltage < 0 or voltage > 1000:
            raise ValueError

        # Check if interlock circuit is open and a voltage of > 21 V is intended to apply (software safety)
        if not int(self.get_interlock_state()) and voltage > 21:
            raise InterlockError

        # Set given voltage
        try:
            query = str(':SOUR:VOLT ' + str(voltage))
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def get_current(self):

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Initialize vars
        result = 0
        i = 0

        # Try to read current. If an error occurs, try it again 5x with an interval of 1 second. Return 0 otherwise.
        # This helps to keep the gui responsive when a communication error occurs. Don't change!
        while i < 5:
            try:
                self.session.write('MEAS:CURR:DC?')
                time.sleep(0.1)
                result = self.session.read()
                break
            except VisaIOError:
                i += 1
                print("ERROR WHILE READING CURRENT. VisaIOError in function electrometer_control.get_current()")
                time.sleep(1)

        return result

    def get_temperature(self):
        """ Read the temperature of the K-Sensor in °C

        :return: Temperature in °C
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to read the temperature
        try:
            self.session.write('SYST:TEMP?')
            temp = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return temp

    def get_interlock_state(self):
        """ Reads the interlock state and returns if open or closed

        :exception InterlockError: If interlock state result is undefined
        :return: True (closed -> HV enabled) or False (open -> HV disabled)
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Get interlock state
        try:
            self.session.write('SYST:INT:TRIP?')
            interlock_state = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        # Map the result to True (interlock closed) or False (interlock open)
        if int(interlock_state) == 0:
            return True
        elif int(interlock_state) == 1:
            return False
        else:
            raise InterlockError

    def enable_source_output(self):
        """ Enable the voltage source (internal relay)

        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to enable the voltage source
        try:
            query = str(':OUTP:STAT ON')
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def disable_source_output(self):
        """ Disable the voltage source.

        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to disable the voltage source
        try:
            query = str(':OUTP:STAT OFF')
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def enable_current_input(self):
        """ Enables the amperemeter input (internal relay)

        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to enable the amperemeter
        try:
            query = str('INP:STAT ON')
            self.session.write(query)
            self.ampmeter_state = True
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def disable_current_input(self):
        """ Disables the amperemeter input

        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to disable the amperemter (connect input internally to gnd)
        try:
            query = str('INP:STAT OFF')
            self.session.write(query)
            self.ampmeter_state = False
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def set_speed(self, speed):
        """ Method for setting the aperture mode (measurement speed). Choose 'stable' for best resolution.

        :param speed: must be string 'quick', 'normal' or 'stable'
        :exception TypeError: If speed is not string
        :exception ValueError: If speed string or not valid
        :return: None
        """

        # Check input parameters
        if not isinstance(speed, str):
            raise TypeError

        speed_strings = ['quick', 'normal', 'stable']
        if speed not in speed_strings:
            raise ValueError

        # Prepare parameter
        if speed == 'quick':
            param = 'SHOR'
        elif speed == 'normal':
            param = 'MED'
        else:
            param = 'LONG'

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to set the speed
        try:
            query = str('SENS:CURR:APER:AUTO:MODE ' + param)
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def set_range(self, range_number):
        """ Method for setting the measurement range.
        Assignment is as follows:
        range_number:   [  0     1     2      3       4     5      6      7      8      9      10     11 ]
        MAX_Value:      [auto, 2 pA, 20 pA, 200 pA, 2 nA, 20 nA, 200 nA, 2 uA, 20 uA, 200 uA, 2 mA, 20 mA]

        :param range_number: measurement range, must be int 200, string 'quick', 'normal' or 'stable'
        :exception TypeError: If range is not  is not string
        :exception ValueError: If speed string or not valid
        :return: None
        """

        # Check input parameters
        if not isinstance(range_number, int):
            raise TypeError

        if range_number < 0 or range_number > 11:
            raise ValueError

        # Check saved range
        if self.range < 0 or self.range > 11:
            raise ValueError

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # Try to set the speed to auto
        if range_number == 0:
            try:
                query = str('SENS:CURR:RANG:AUTO 1')
                self.session.write(query)
                self.range_mode = 'auto'
            except visa.Error:
                self.connection_state = False
                self.close_connection()
                return False
        else:
            # detect if mode was auto in the last call, and if so, initialize manual mode range to MAX
            if self.range_mode == 'auto':
                try:
                    query = str('SENS:CURR:RANG:UPP MAX')
                    self.session.write(query)
                    self.range = 11
                    print("reset range to MAX")
                    self.range_mode = 'manual'
                except visa.Error:
                    self.connection_state = False
                    self.close_connection()
                    return False

            # disable auto range
            try:
                query = str('SENS:CURR:RANG:AUTO 0')
                self.session.write(query)
            except visa.Error:
                self.connection_state = False
                self.close_connection()
                return False

            if range_number > self.range:
                # increase range until desired range is reached
                while range_number > self.range:
                    try:
                        query = str('SENS:CURR:RANG:UPP UP')
                        self.session.write(query)
                        self.range += 1
                    except visa.Error:
                        self.connection_state = False
                        self.close_connection()
                        return False

            elif range_number < self.range:
                # decrease range until desired range is reached
                while range_number < self.range:
                    try:
                        query = str('SENS:CURR:RANG:UPP DOWN')
                        self.session.write(query)
                        self.range -= 1
                    except visa.Error:
                        self.connection_state = False
                        self.close_connection()
                        return False

            else:
                raise ValueError

    def close_connection(self):
        """ Closes the usb connection (session and resource manager) and resets the connection state var

        :return: None
        """

        # Close the connection to the instrument
        try:
            self.session.close()
            self.rm.close()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        if Parameters.DEBUG:
            print("Connection closed")

