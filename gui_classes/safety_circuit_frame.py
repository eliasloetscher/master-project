import tkinter as tk
from parameters import Parameters


class SafetyCircuitFrame:
    """ This class implements the gui widget for the saftey circuit section.

    Methods
    ---------
    auto_update_labels()    Starts to periodically update the gui state labels (safety circuit frame)
    """

    def __init__(self, root, labjack, relays):
        """Constructor of the class ControlFrame

        For the following device parameters, use the corresponding class in the package 'devices'
        :param root: tkinter root instance
        :param labjack: object for controlling the labjack
        :param relays: object for controlling the relays
        """

        # initialize class vars
        self.root = root
        self.labjack = labjack
        self.relays = relays

        # initialize and place frame
        self.safety_circuit_frame = tk.Frame(self.root, width=430, height=200, highlightbackground="black",
                                             highlightthickness=1)
        self.safety_circuit_frame.grid(row=2, padx=20, pady=(0, 20))

        # avoid frame shrinking to the size of the included elements
        self.safety_circuit_frame.grid_propagate(False)

        # set and place frame title
        safety_frame_title = tk.Label(self.safety_circuit_frame, text="Safety Circuit", font="Helvetica 14 bold")
        safety_frame_title.grid(padx=5, pady=5, sticky="W", columnspan=2)

        # place S1 state label
        tk.Label(self.safety_circuit_frame, text="Test cell:").grid(row=1, sticky="W", padx=(10, 0))
        self.s1_state_label = tk.Label(self.safety_circuit_frame, text="n/a")
        self.s1_state_label.grid(row=1, column=1, sticky="W", padx=(12, 0))

        # place S2 state label
        tk.Label(self.safety_circuit_frame, text="HV box:").grid(row=2, sticky="W", padx=(10, 0), pady=(10, 0))
        self.s2_state_label = tk.Label(self.safety_circuit_frame, text="n/a")
        self.s2_state_label.grid(row=2, column=1, sticky="W", padx=(12, 0), pady=(10, 0))

        # place relay state label
        tk.Label(self.safety_circuit_frame, text="Safety relay:").grid(row=3, sticky="W", padx=(10, 0), pady=(10, 0))
        self.relay_state_label = tk.Label(self.safety_circuit_frame, text="n/a")
        self.relay_state_label.grid(row=3, column=1, sticky="W", padx=(12, 0), pady=(10, 0), columnspan=2)

        # set and place 'close' or 'open' safety circuit buttons
        open_button = tk.Button(self.safety_circuit_frame, text="Open", width=7, command=lambda: relays.switch_relay("SAFETY", "OFF", labjack))
        close_button = tk.Button(self.safety_circuit_frame, text="Close", width=7, command=lambda: relays.switch_relay("SAFETY", "ON", labjack))
        open_button.place(x=185, y=102)
        close_button.place(x=262, y=102)

        # place label for safety_message
        self.safety_message = tk.Label(self.safety_circuit_frame, text="", fg="red")
        self.safety_message.grid(row=4, sticky="W", padx=10, pady=(20, 0), columnspan=3)

        # initialize safety state frame
        self.state_frame = tk.Frame(self.safety_circuit_frame, width=50, height=50, highlightbackground="black",
                                    highlightthickness=1, bg="green")
        self.state_frame.place(x=360, y=130)

        # start to update labels periodically
        self.auto_update_labels()

    def auto_update_labels(self):
        """ Starts to periodically update the gui state labels (safety circuit frame)

        :return: None
        """

        # get states
        s1_state = self.labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
        s2_state = self.labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
        relay_state_text = self.relays.safety_state

        # handle error messages (remember no/nc switch mechanisms HIGH/LOW)
        if s1_state == "HIGH" and s2_state == "LOW" and not self.relays.safety_message == "":
            # clear error message
            self.relays.safety_message = ""
            if Parameters.DEBUG:
                print("cleared safety error message")
        self.safety_message.configure(text=self.relays.safety_message)

        # prepare s1 label text (switch: normally closed)
        if s1_state == "HIGH":
            s1_label_text = "closed"
        elif s1_state == "LOW":
            s1_label_text = "open"
        elif not s1_state:
            # if labjack is not connected, s1_state is False
            s1_label_text = "n/a"
        else:
            raise ValueError

        # prepare s2 label text (switch: normally open)
        if s2_state == "LOW":
            s2_label_text = "closed"
        elif s2_state == "HIGH":
            s2_label_text = "open"
        elif not s2_state:
            # if labjack is not connected, s1_state is False
            s2_label_text = "n/a"
        else:
            raise ValueError

        # check text of relay_state
        if not relay_state_text == "closed" and not relay_state_text == "open":
            raise ValueError

        # prepare label colours
        label_text = [s1_label_text, s2_label_text, relay_state_text]
        label_colours = []
        for element in label_text:
            if element == "closed":
                label_colours.append("red")
            elif element == "open":
                label_colours.append("green")
            elif element == "n/a":
                label_colours.append("black")
            else:
                raise ValueError

        # check if label colours list is valid
        if len(label_colours) != 3:
            raise ValueError

        # update labels
        self.s1_state_label.configure(text=s1_label_text, fg=label_colours[0])
        self.s2_state_label.configure(text=s2_label_text, fg=label_colours[1])
        self.relay_state_label.configure(text=relay_state_text, fg=label_colours[2])

        # update state frame
        if s1_label_text == 'closed' and s2_label_text == 'closed' and relay_state_text == 'closed':
            self.state_frame.configure(bg="red")
        else:
            self.state_frame.configure(bg="green")

        # repeat at a given time interval
        self.root.after(500, self.auto_update_labels)
