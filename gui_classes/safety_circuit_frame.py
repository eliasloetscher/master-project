import tkinter as tk
from mviss_module.parameters import Parameters


class SafetyCircuitFrame:
    """ This class implements the gui widget for the safety circuit.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions, labjack, relays):
        """ Constructor of the safety circuit class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.safety_circuit_frame = tk.Frame(self.master, width=430, height=200, highlightbackground="black",
                                             highlightthickness=1)
        self.safety_circuit_frame.grid(row=2, padx=20, pady=(0, 20))
        self.safety_circuit_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

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
        open_button.grid(row=3, column=2, sticky="W", pady=(10, 0), padx=(20, 0))
        close_button.grid(row=3, column=3, sticky="W", pady=(10, 0), padx=(5, 0))

        # Initialize safety state frame
        self.state_frame = tk.Frame(self.safety_circuit_frame, width=50, height=50, highlightbackground="black",
                                    highlightthickness=1, bg="green")
        self.state_frame.place(x=370, y=100)

    def auto_update_labels(self, root, labjack, relays):
        """

        :param root:
        :param labjack:
        :param relays:
        :return:
        """

        # Get states
        s1_state = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S1)
        s2_state = labjack.read_digital(Parameters.LJ_DIGITAL_IN_PILZ_S2)
        relay_state_text = relays.safety_state

        # Prepare s1 label text
        if s1_state == "HIGH":
            s1_label_text = "closed"
        elif s1_state == "LOW":
            s1_label_text = "open"
        else:
            raise ValueError

        # Prepare s2 label text
        if s2_state == "HIGH":
            s2_label_text = "closed"
        elif s2_state == "LOW":
            s2_label_text = "open"
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
            else:
                raise ValueError

        # Check if label colours list is valid
        if len(label_colours) != 3:
            raise ValueError

        # Update labels
        self.s1_state_label.configure(text=s1_label_text, fg=label_colours[0])
        self.s2_state_label.configure(text=s2_label_text, fg=label_colours[1])
        self.relay_state_label.configure(text=relay_state_text, fg=label_colours[2])

        # Update state frame
        if s1_label_text == 'closed' and s2_label_text == 'closed' and relay_state_text == 'closed':
            self.state_frame.configure(bg="red")
        else:
            self.state_frame.configure(bg="green")

        # repeat with a given time interval
        root.after(500, lambda: self.auto_update_labels(root, labjack, relays))
