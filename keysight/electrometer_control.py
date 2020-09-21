import pyvisa as visa
from mviss_package.parameters import Parameters
from pyvisa import constants


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

        if int(self.get_interlock_state()) == 1 and voltage > 21 :
            raise InterlockError

        query = str(':SOUR:VOLT ' + str(voltage))
        self.session.write(query)

    def get_current(self):
        self.session.write('MEAS:CURR:DC?')
        return self.session.read()

    def get_temperature(self):
        """
        :return:
        """
        self.session.write('SYST:TEMP?')
        return self.session.read()

    def get_interlock_state(self):
        """
        Reads the interlock state and returns if open or closed
        :return: 0 (close) or 1 (open)
        """
        self.session.write('SYST:INT:TRIP?')
        return self.session.read()

    def close_connection(self):
        # Close the connection to the instrument
        self.session.close()
        self.rm.close()

        if self.DEBUG:
            print("Connection closed")
