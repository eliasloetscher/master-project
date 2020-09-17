import pyvisa as visa
from mviss_package.parameters import Parameters


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

    def close_connection(self):
        # Close the connection to the instrument
        self.session.close()
        self.rm.close()

        if self.DEBUG:
            print("Connection closed")
