

class Parameters:
    """ This class defines all parameters which are used in the mviss resistivity measurement test setup.

    Methods
    ---------
    None

    """
    def __init__(self):
        """ Constructor of the Parameters class.

        """
        pass

    # Is a boolean which defines, if the programs should run in debug mode (True) or not (False)
    DEBUG = True

    # Breakdown detection voltage deviation in % (bd is detected if voltage_is deviates mor than x% from voltage_set)
    BD_VOLTAGE_DEVIATION = 10

    # Breakdown detection current limit in mA (bd is detected when current_is > current_limit)
    BD_CURRENT_LIMIT = 10

    # Breakdown interval in seconds specifies how often the routine checks for a breakdown
    BD_INTERVAL = 2

    # Keysight VISA address
    KEYSIGHT_VISA_ADDRESS = "USB0::0x0957::0xD518::MY54321380::0::INSTR"

    # Labjack serial number
    LABJACK_SERIAL_NUMBER = "470019966"

    # Labjack connection type
    LABJACK_CONNECTION = "USB"

    # Labjack model
    LABJACK_MODEL = "T7"

    # Location for logfiles
    LOCATION_LOG_FILES = "C:/Users/eliasl/Documents/logfiles/"

    # Labjack analog input port for hv probe
    LJ_ANALOG_IN_HV_PROBE = "AIN0"

    # Labjack analog input port for humidity sensor (integrated in htm2500lf)
    LJ_ANALOG_IN_HUMIDITY_SENSOR = "AIN11"

    # Labjack analog input port for temperature sensor (integrated in htm2500lf)
    LJ_ANALOG_IN_TEMP_SENSOR = "AIN10"

    # Labjack analog input port for hvamp
    LJ_ANALOG_IN_HVAMP_VOLTAGE = "AIN2"
    LJ_ANALOG_IN_HVAMP_CURRENT = "AIN3"

    # Labjack digital output port for hv_enable (part of safety circuit)
    LJ_DIGITAL_OUT_SAFETY_RELAY = "FIO0"

    # Labjack digital output port for gnd_relay
    LJ_DIGITAL_OUT_GND_RELAY = "FIO1"

    # Labjack digital output port for hv_relay
    LJ_DIGITAL_OUT_HV_RELAY = "FIO2"

    # Labjack digital output port for signal lamps
    LJ_DIGITAL_OUT_SIGNAL_LAMP = "FIO3"

    # Labjack digital input port for Pilz S1 state
    LJ_DIGITAL_IN_PILZ_S1 = "FIO4"

    # Labjack digital input port for Pilz S2 state
    LJ_DIGITAL_IN_PILZ_S2 = "FIO5"

    # Labjack Tick DAC connection for I2C Communication. Lower Pin is SCL, Higher Pin is SDA. Corresponds to FIO Pins.
    LJ_TICK_DAC_DOUT_SCL = "6"
    LJ_TICK_DAC_DOUT_SDA = "7"

    # Labjack tick dac analog out channels for hvamp
    LJ_ANALOG_OUT_HVA_REF = "A"
    LJ_ANALOG_OUT_HVA_CTRL = "B"
