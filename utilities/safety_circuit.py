"""
Safety circuit module
"""
from parameters import Parameters
import tkinter.messagebox


def start_safety_circuit(root, labjack, relays):
    """

    :param root:
    :param labjack:
    :param relays:
    :return:
    """

    # Switch off all relays and assure correct functionality
    assert relays.switch_off_all_relays()

    # start the safety circuit with auto update
    auto_update_safety_circuit(root, labjack, relays, labjack.connection_state)


def auto_update_safety_circuit(root, labjack, relays, labjack_state_before):
    """

    :param root:
    :param labjack:
    :param relays:
    :return:
    """

    # Get labjack state
    labjack_state_now = labjack.connection_state

    # Detect labjack reconnection
    if not labjack_state_before and labjack_state_now:
        if Parameters.DEBUG:
            print("safety circuit: labjack reconnection detected")
        # Switch off all relays to ensure safety and correct label states
        relays.switch_off_all_relays()

    # Read states of safety elements
    state_s1 = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
    state_s2 = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
    state_safety_relay = relays.safety_state
    state_hv_relay = relays.hv_relay_state
    state_gnd_relay = relays.gnd_relay_state

    # Switch off safety relay and hv relay if S1 or S2 is opened
    if state_s1 == "LOW" or state_s2 == "LOW":
        if state_safety_relay == "closed":
            relays.switch_relay("SAFETY", "OFF", labjack)
        if state_hv_relay == "closed":
            relays.switch_relay("HV", "OFF", labjack)

    # Switch off gnd/hv relays if safety circuit is opened
    if state_s1 == "LOW" or state_s2 == "LOW" or state_safety_relay == "open":
        print(state_hv_relay, state_gnd_relay)
        if state_hv_relay == "closed":
            relays.switch_relay("HV", "OFF", labjack)
        if state_gnd_relay == "closed":
            relays.switch_relay("GND", "OFF", labjack)

    # Switch signal lamp (note: if state is HIGH, switch is closed! State 'ON' means switch to red)
    if state_s1 == "HIGH" and state_s2 == "HIGH" and state_safety_relay == "closed":
        if relays.lamp_state == "open":
            print("safety circuit: switch lamp to red")
            relays.switch_relay("LAMP", "ON", labjack)
    else:
        if relays.lamp_state == "closed":
            print("safety circuit: switch lamp to green")
            relays.switch_relay("LAMP", "OFF", labjack)

    # Check safety circuit periodically (given in ms)
    root.after(500, lambda: auto_update_safety_circuit(root, labjack, relays, labjack_state_now))
