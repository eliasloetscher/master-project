"""
Safety circuit module
"""
from parameters import Parameters


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
    auto_update_safety_circuit(root, labjack, relays)


def auto_update_safety_circuit(root, labjack, relays):
    """

    :param root:
    :param labjack:
    :param relays:
    :return:
    """

    # Read states of safety elements
    state_s1 = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
    state_s2 = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
    state_safety_relay = relays.safety_state

    # Switch off safety relay if S1 or S2 is opened
    if state_s1 == "LOW" or state_s2 == "LOW":
        relays.switch_relay("SAFETY", "OFF", labjack)

    # Switch signal lamp (note: if state is HIGH, switch is closed!)
    if state_s1 == "HIGH" and state_s2 == "HIGH" and state_safety_relay == "closed":
        relays.switch_relay("LAMP", "ON", labjack)
    else:
        relays.switch_relay("LAMP", "OFF", labjack)

    # Check safety circuit periodically (given in ms)
    root.after(500, lambda: auto_update_safety_circuit(root, labjack, relays))
