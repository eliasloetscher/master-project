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

        # Initialize class vars
        self.root = root
        self.labjack = labjack
        self.relays = relays

        # Initialize and place frame
        self.safety_circuit_frame = tk.Frame(self.root, width=430, height=200, highlightbackground="black",
                                             highlightthickness=1)
        self.safety_circuit_frame.grid(row=2, padx=20, pady=(0, 20))

        # Avoid frame shrinking to the size of the included elements
        self.safety_circuit_frame.grid_propagate(False)

        # Set and place frame title
        safety_frame_title = tk.Label(self.safety_circuit_frame, text="Safety Circuit", font="Helvetica 14 bold")
        safety_frame_title.grid(padx=5, pady=5, sticky="W", columnspan=2)

        # Place S1 state label
        tk.Label(self.safety_circuit_frame, text="Pilz S1:").grid(row=1, sticky="W", padx=(10, 0))
        self.s1_state_label = tk.Label(self.safety_circuit_frame, text="n/a")
        self.s1_state_label.grid(row=1, column=1, sticky="W", padx=(12, 0))

        # Place S2 state label
        tk.Label(self.safety_circuit_frame, text="Pilz S2:").grid(row=2, sticky="W", padx=(10, 0), pady=(10, 0))
        self.s2_state_label = tk.Label(self.safety_circuit_frame, text="n/a")
        self.s2_state_label.grid(row=2, column=1, sticky="W", padx=(12, 0), pady=(10, 0))

        # Place relay state label
        tk.Label(self.safety_circuit_frame, text="Safety relay:").grid(row=3, sticky="W", padx=(10, 0), pady=(10, 0))
        self.relay_state_label = tk.Label(self.safety_circuit_frame, text="n/a")
        self.relay_state_label.grid(row=3, column=1, sticky="W", padx=(12, 0), pady=(10, 0), columnspan=2)

        # Set and place 'close' or 'open' safety circuit buttons
        open_button = tk.Button(self.safety_circuit_frame, text="Open", width=7, command=lambda: relays.switch_relay("SAFETY", "OFF", labjack))
        close_button = tk.Button(self.safety_circuit_frame, text="Close", width=7, command=lambda: relays.switch_relay("SAFETY", "ON", labjack))
        open_button.place(x=185, y=102)
        close_button.place(x=262, y=102)

        # Place label for safety_message
        self.safety_message = tk.Label(self.safety_circuit_frame, text="", fg="red")
        self.safety_message.grid(row=4, sticky="W", padx=10, pady=(20, 0), columnspan=3)

        # Initialize safety state frame
        self.state_frame = tk.Frame(self.safety_circuit_frame, width=50, height=50, highlightbackground="black",
                                    highlightthickness=1, bg="green")
        self.state_frame.place(x=360, y=130)

        # Start to update labels periodically
        self.auto_update_labels()

    def auto_update_labels(self):
        """ Starts to periodically update the gui state labels (safety circuit frame)

        :return: None
        """

        # Get states
        s1_state = self.labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
        s2_state = self.labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
        relay_state_text = self.relays.safety_state

        # Prepare s1 label text (switch: normally closed)
        if s1_state == "HIGH":
            s1_label_text = "closed"
            # Clear error message
            if not self.relays.safety_message == "":
                self.relays.safety_message = ""
                if Parameters.DEBUG:
                    print("cleared safety error message")
        elif s1_state == "LOW":
            s1_label_text = "open"
        elif not s1_state:
            # If labjack is not connected, s1_state is False
            s1_label_text = "n/a"
        else:
            raise ValueError

        # Prepare s2 label text (switch: normally open)
        if s2_state == "LOW":
            s2_label_text = "closed"
        elif s2_state == "HIGH":
            s2_label_text = "open"
        elif not s2_state:
            # If labjack is not connected, s1_state is False
            s2_label_text = "n/a"
        else:
            raise ValueError

        # Check text of relay_state
        if not relay_state_text == "closed" and not relay_state_text == "open":
            raise ValueError

        # Prepare label colours
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

        # Check if label colours list is valid
        if len(label_colours) != 3:
            raise ValueError

        # Update labels
        self.s1_state_label.configure(text=s1_label_text, fg=label_colours[0])
        self.s2_state_label.configure(text=s2_label_text, fg=label_colours[1])
        self.relay_state_label.configure(text=relay_state_text, fg=label_colours[2])
        self.safety_message.configure(text=self.relays.safety_message)

        # Update state frame
        if s1_label_text == 'closed' and s2_label_text == 'closed' and relay_state_text == 'closed':
            self.state_frame.configure(bg="red")
        else:
            self.state_frame.configure(bg="green")

        # Repeat at a given time interval
        self.root.after(500, self.auto_update_labels)
