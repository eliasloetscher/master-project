"""
This module provides all the software safety measures of the mviss test setup.
It is validated as part of the master thesis by Elias Loetscher.

-> Only change this module if you know what you're doing!
Test setup safety has to be rechecked by Fabian Mächler if you make changes in this module!
"""
from parameters import Parameters


def start_safety_circuit(root, labjack, relays, electrometer, hvamp):
    """ This method needs to be called at safety circuit startup.
    It switches off all relays assuring the correct initial states ('off').
    After that, the automatic update of the safety circuit is started.

    :param root: GUI instance
    :param labjack: instance of the class LabjackConnection
    :param relays: instance of the class Relays
    :param electrometer: instance of the class Electrometer
    :param hvamp; instance of the class HVAmp
    :return: None
    """

    # Switch off all relays and assure correct functionality
    assert relays.switch_off_all_relays()

    # start the safety circuit with auto update
    auto_update_safety_circuit(root, labjack, relays, electrometer, hvamp, labjack.connection_state)


def auto_update_safety_circuit(root, labjack, relays, electrometer, hvamp, labjack_state_before):
    """ This method assures the correct operation of the safety circuit.
    It is called and repeated every 200 ms after the first startup.

    :param root: GUI instance
    :param labjack: instance of the class LabjackConnection
    :param relays: instance of the class relays
    :param electrometer: instance of the class Electrometer
    :param hvamp; instance of the class HVAmp
    :param labjack_state_before: flag for detecting if the labjack is reconnected after connection loss
    :return:
    """

    # get labjack state
    labjack_state_now = labjack.connection_state

    # detect labjack reconnection
    if not labjack_state_before and labjack_state_now:
        if Parameters.DEBUG:
            print("safety circuit: labjack reconnection detected")
        # switch off all relays to ensure safety and correct label states
        relays.switch_off_all_relays()

    # read states of safety elements
    state_s1 = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
    state_s2 = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
    state_safety_relay = relays.safety_state
    state_hv_relay = relays.hv_relay_state
    state_gnd_relay = relays.gnd_relay_state

    # --- ACTIONS IF SAFETY SWITCH S1 OR S2 IS OPENED --- #
    # switch off safety relay and hv relay if S1 or S2 is opened -> Watch out, not same Pilz version (opener/closer)
    if state_s1 == "LOW" or state_s2 == "HIGH":
        # switch off safety relay
        if state_safety_relay == "closed":
            relays.switch_relay("SAFETY", "OFF", labjack)
        if state_hv_relay == "closed":
            relays.switch_relay("HV", "OFF", labjack)

    # --- ACTIONS IF SAFETY CIRCUIT IS CLOSED --- #
    # Switch signal lamp if all three safety switches are closed.
    # Watch out, not same Pilz version (opener/closer)!
    # S1: HIGH is closed.
    # S2: LOW is closed.
    if state_s1 == "HIGH" and state_s2 == "LOW" and state_safety_relay == "closed":
        # send command only if lamp is green right now
        if relays.lamp_state == "open":
            # print action if debug mode is on
            if Parameters.DEBUG:
                print("safety circuit: switch lamp to red")
            # State 'ON' means switch to red)
            relays.switch_relay("LAMP", "ON", labjack)

    # --- ELSE CONDITION: AT LEAST ONE SAFETY ELEMENT (S1, S2, SAFETY_RELAY) IS OPEN
    else:
        # --- PERIODIC ACTIONS WHEN SAFETY CIRCUIT IS OPEN --- #
        # open HV relay if closed right now
        if state_hv_relay == "closed":
            relays.switch_relay("HV", "OFF", labjack)

        # close GND relay if open right now
        if state_gnd_relay == "open":
            relays.switch_relay("GND", "ON", labjack)

        # --- ONE TIME ACTIONS WHEN SAFETY CIRCUIT IS OPENED --- #
        # this can be detected due to the else-condition in combination with the lamp still in red mode
        # one time actions are performed in order to avoid overloading the electrometer/hvamp communication
        # this is not safety critical, it is anyway not possible to switch on the electrometer/hvamp (-> HW interlock)
        # it is performed to assure that the voltage is set to zero after (re-)closing the safety circuit
        if relays.lamp_state == "closed":
            # switch lamp to green ('OFF') if red right now
            relays.switch_relay("LAMP", "OFF", labjack)

            # reset hvamp voltage to zero
            hvamp.set_voltage(0)

            # reset electrometer voltage to zero and switch off voltage source
            electrometer.set_voltage(0)
            electrometer.disable_source_output()

            # disable ammeter
            electrometer.disable_current_input()

    # Check safety circuit periodically (given in ms)
    root.after(200, lambda: auto_update_safety_circuit(root, labjack, relays, electrometer, hvamp, labjack_state_now))
