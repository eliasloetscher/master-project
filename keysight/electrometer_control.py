import pyvisa as visa
from mviss_module.parameters import Parameters
from pyvisa import constants
from pyvisa import VisaIOError


class InterlockError(Exception):
    """ Exception raised when an action is not possible due to open or closed interlock
        Example: Trying to set voltage >26 V when interlock is open
    """
    pass


class ElectrometerControl:

    def __init__(self):
        """

        """

        # Electrometer session (default: None. If connected: electrometer session instance)
        self.session = None

        # Electrometer connection state (default: None, connection_error: False, connected: True)
        self.connection_state = False

        # Electrometer resource manager
        self.rm = None

        # Try to connect
        self.connect()

    def connect(self):
        """ Function used for connecting to Keysight electrometer with parameters specified in Parameters class

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
        """

        :return:
        """
        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            return False

        try:
            self.session.write('SYST:COMM:ENAB? USB')
            result = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return result

    def get_idn_response(self):
        """
        :return: idn response as String
        """

        try:
            # Try to read IDN response
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
        """
        :return:
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
        Sets the source voltage immediately.
        Raises ValueError if voltage is out of range (<0 V or >1000 V)
        Raises InterlockError if voltage is > 21 V and interlock is open
        :param voltage: Voltage to set
        :return: None
        """
        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        if voltage < 0 or voltage > 1000:
            raise ValueError

        if not int(self.get_interlock_state()) and voltage > 21:
            raise InterlockError

        try:
            query = str(':SOUR:VOLT ' + str(voltage))
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def enable_source_output(self):
        """
        Enables the voltage source.
        :return: None
        """
        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        try:
            query = str(':OUTP:STAT ON')
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def disable_source_output(self):
        """
        Disables the voltage source.
        :return: None
        """
        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        try:
            query = str(':OUTP:STAT OFF')
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def enable_current_input(self):
        """
        Enables the amperemeter input
        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        try:
            query = str('INP:STAT ON')
            self.session.write(query)
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

    def disable_current_input(self):
        """
        Disables the amperemeter input
        :return: None
        """

        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        try:
            query = str('INP:STAT OFF')
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

        try:
            self.session.write('MEAS:CURR:DC?')
            result = self.session.read()
        except VisaIOError:
            print("ERROR WHILE READING CURRENT. VisaIOError in function electrometer_control.get_current()")
            result = 0

        return result

    def get_temperature(self):
        """
        :return:
        """
        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        try:
            self.session.write('SYST:TEMP?')
            temp = self.session.read()
        except visa.Error:
            self.connection_state = False
            self.close_connection()
            return False

        return temp

    def get_interlock_state(self):
        """
        Reads the interlock state and returns if open or closed
        :return: True (closed -> HV enabled) or False (open -> HV disabled)
        """
        # Check if connection is alive. If not, try to connect.
        if not self.connection_state:
            if not self.connect():
                return False

        self.session.write('SYST:INT:TRIP?')
        interlock_state = self.session.read()
        if int(interlock_state) == 0:
            return True
        elif int(interlock_state) == 1:
            return False
        else:
            raise InterlockError

    def close_connection(self):
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

