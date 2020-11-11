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
        self.ADDR = Parameters.KEYSIGHT_VISA_ADDRESS
        self.DEBUG = Parameters.DEBUG

        # Setup a connection
        try:
            # Create a connection (session) to the instrument
            if self.DEBUG:
                print("Connecting to KEYSIGHT B2985A with addr: ", self.ADDR, " ...")
            self.rm = visa.ResourceManager()
            self.session = self.rm.open_resource(self.ADDR)
            if self.DEBUG:
                print("Successful! Created visa session.")
        except visa.Error as ex:
            if self.DEBUG:
                print("Couldn't connect!")
            pass

    def get_idn_response(self):
        """
        :return: idn response as String
        """

        # Send *IDN? and read the response
        self.session.write('*IDN?')
        idn = self.session.read()

        if self.DEBUG:
            print('*IDN? returned: %s' % idn.rstrip('\n'))

    def get_voltage(self):
        """
        :return:
        """
        self.session.write('MEAS:VOLT:DC?')
        return self.session.read()

    def set_voltage(self, voltage):
        """
        Sets the source voltage immediately.
        Raises ValueError if voltage is out of range (<0 V or >1000 V)
        Raises InterlockError if voltage is > 21 V and interlock is open
        :param voltage: Voltage to set
        :return: None
        """
        if voltage < 0 or voltage > 1000:
            raise ValueError

        if not int(self.get_interlock_state()) and voltage > 21:
            raise InterlockError

        query = str(':SOUR:VOLT ' + str(voltage))
        self.session.write(query)

    def enable_source_output(self):
        """
        Enables the voltage source.
        :return: None
        """

        query = str(':OUTP:STAT ON')
        self.session.write(query)

    def disable_source_output(self):
        """
        Disables the voltage source.
        :return: None
        """

        query = str(':OUTP:STAT OFF')
        self.session.write(query)

    def enable_current_input(self):
        """
        Enables the amperemeter input
        :return: None
        """
        query = str('INP:STAT ON')
        self.session.write(query)

    def disable_current_input(self):
        """
        Disables the amperemeter input
        :return: None
        """
        query = str('INP:STAT OFF')
        self.session.write(query)
        print("Disbled ASDFASDFASDFNASJKDFB")

    def get_current(self):
        self.session.write('MEAS:CURR:DC?')
        try:
            result = self.session.read()
        except VisaIOError:
            print("ERROR WHILE READING CURRENT. VisaIOError in function electrometer_control.get_current()")
            result = 0

        return result

    def get_temperature(self):
        """
        :return:
        """
        self.session.write('SYST:TEMP?')
        return self.session.read()

    def get_interlock_state(self):
        """
        Reads the interlock state and returns if open or closed
        :return: True (closed -> HV enabled) or False (open -> HV disabled)
        """
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
        self.session.close()
        self.rm.close()

        if self.DEBUG:
            print("Connection closed")
