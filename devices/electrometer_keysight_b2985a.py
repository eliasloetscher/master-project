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
    """ This class provides a set of methods in order to control the electrometer Keysight B2985A via USB.
    The communication is based on scpi and the valid keywords are specified in the 'scpi reference guide',
    available online.

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
    enable_current_input()  Enables the ammeter (internal relay)
    disable_current_input() Disables the ammeter (i.e. internally connected to gnd)
    set_voltage_range()     Sets the voltage output range to -1 kV or to + 1 kV
    set_speed()             Sets the measurement speed ('quick', 'normal', 'stable')
    set_range()             Sets the current measurement range
    close_connection()      Closes the usb connection and resets the state variables
    """

    def __init__(self):
        """ Constructor of the class ElectrometerControl with initialization of class vars.

        """

        # electrometer session (default: None. If connected: electrometer session instance)
        self.session = None

        # electrometer connection state (default: None, connection_error: False, connected: True)
        self.connection_state = False

        # electrometer resource manager
        self.rm = None

        # state of the ampere meter: enabled (True) or disabled (False)
        self.ampmeter_state = False

        # initialize var for voltage set by user in V
        self.user_voltage = 0

        # measurement range variable (0 corresponds to 'auto')
        self.range = 0
        self.range_mode = 'auto'

        # measurement speed variable, default must be 'normal'. options are ('quick', 'normal', 'stable')
        self.speed = 'normal'

        # store previous voltage
        self.previous_voltage = 0

        # Try to connect
        self.connect()

    def connect(self):
        """ Function used for connecting to Keysight electrometer with address specified in Parameters class.

        :return: True if connection successful, False if connection error occurred
        """

        # check if already connected
        if self.connection_state:
            if Parameters.DEBUG:
                print("Function electrometer_control.connect: already connected!")
            return True

        # setup a connection
        try:
            # create a connection (session) to the instrument
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
        """ This method checks if the connection is still alive and if not, a reconnection attempt is made.

        :return: False if connection is not alive, True otherwise
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            return False

        # try to ask if the usb connection is enabled. If an error occurs, the connection is down.
        try:
            self.session.write('SYST:COMM:ENAB? USB')
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return True

    def get_idn_response(self):
        """ Returns the electrometer idn response (system information).

        :return: idn response as String
        """

        # try to read IDN response
        try:
            self.session.write('*IDN?')
            idn = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        # print idn response
        if Parameters.DEBUG:
            print('*IDN? returned: %s' % idn.rstrip('\n'))

        return idn

    def get_voltage(self):
        """ Reads the voltage of the internal voltage source in V.

        :return: False if connection is not alive, voltage in V otherwise
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to read voltage
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

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # check input parameter, maximum output voltage is +/- 1000 V
        if voltage < -1000 or voltage > 1000:
            raise ValueError

        # set voltage output range (electrometer parameter) to - 1 kV or + 1 kV respectively
        if self.previous_voltage < 5 and voltage >= 0:
            self.disable_source_output()
            time.sleep(0.1)
            self.set_voltage_range(1)
            time.sleep(0.1)
            self.enable_source_output()
        elif self.previous_voltage > -5 and voltage < 0:
            self.disable_source_output()
            time.sleep(0.1)
            self.set_voltage_range(-1)
            time.sleep(0.1)
            self.enable_source_output()

        # set given voltage
        try:
            query = str(':SOUR:VOLT ' + str(voltage))
            self.session.write(query)
            self.user_voltage = voltage
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        self.previous_voltage = voltage

    def get_current(self):
        """ Read and return measured current in A.

        :return: current in A
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # initialize vars
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
                time.sleep(0.5)

        return result

    def get_temperature(self):
        """ Read the temperature of the K-Sensor in °C.

        :return: Temperature in °C
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to read the temperature
        try:
            self.session.write('SYST:TEMP?')
            temp = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return temp

    def get_interlock_state(self):
        """ Reads the interlock state and returns if open or closed.

        :exception InterlockError: If interlock state result is undefined
        :return: True (closed -> HV enabled) or False (open -> HV disabled)
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # get interlock state
        try:
            self.session.write('SYST:INT:TRIP?')
            interlock_state = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        # map the result to True (interlock closed) or False (interlock open)
        if int(interlock_state) == 0:
            return True
        elif int(interlock_state) == 1:
            return False
        else:
            raise InterlockError

    def enable_source_output(self):
        """ Enable the voltage source (internal relay).

        :return: None
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to enable the voltage source
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

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to disable the voltage source
        try:
            query = str(':OUTP:STAT OFF')
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def enable_current_input(self):
        """ Enables the ammeter input (internal relay).

        :return: None
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to enable the ammeter
        try:
            query = str('INP:STAT ON')
            self.session.write(query)
            self.ampmeter_state = True
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def disable_current_input(self):
        """ Disables the ammeter input.

        :return: None
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to disable the amperemter (connect input internally to gnd)
        try:
            query = str('INP:STAT OFF')
            self.session.write(query)
            self.ampmeter_state = False
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def set_voltage_range(self, volt_range):
        """ Set the voltage output range to -1 kV or to +1 kV.

        :param volt_range: int, voltage range, must be 1 for +1 kV or -1 for -1 kV
        :exception ValueError: raised if input parameter is not valid
        :return: None
        """

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        if volt_range == -1:
            write = str('SOUR:VOLT:RANG MIN')
        elif volt_range == 1:
            write = str('SOUR:VOLT:RANG MAX')
        else:
            raise ValueError

        # try to set the voltage range
        try:
            query = write
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

        # check input parameters
        if not isinstance(speed, str):
            raise TypeError

        speed_strings = ['quick', 'normal', 'stable']
        if speed not in speed_strings:
            raise ValueError

        # prepare parameter for scpi command
        if speed == 'quick':
            param = 'SHOR'
        elif speed == 'normal':
            param = 'MED'
        else:
            param = 'LONG'

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to set the speed
        try:
            query = str('SENS:CURR:APER:AUTO:MODE ' + param)
            self.session.write(query)
            self.speed = speed
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

        # check input parameters
        if not isinstance(range_number, int):
            raise TypeError

        if range_number < 0 or range_number > 11:
            raise ValueError

        # check saved range
        if self.range < 0 or self.range > 11:
            raise ValueError

        # check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        # try to set the speed to auto
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
                        time.sleep(0.1)
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
                        time.sleep(0.1)
                    except visa.Error:
                        self.connection_state = False
                        self.close_connection()
                        return False
            elif range_number == self.range:
                pass
            else:
                raise ValueError

    def close_connection(self):
        """ Closes the usb connection (session and resource manager) and resets the connection state var.

        :return: None
        """

        # close the connection to the instrument
        try:
            self.session.close()
            self.rm.close()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        if Parameters.DEBUG:
            print("Connection closed")
