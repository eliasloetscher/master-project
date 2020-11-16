import tkinter as tk


class SafetyCircuitFrame:
    """ This class implements the gui widget for the safety circuit.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions):
        """ Constructor of the safety circuit class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.safety_circuit_frame = tk.Frame(self.master, width=500, height=300, highlightbackground="black",
                                             highlightthickness=1)
        self.safety_circuit_frame.grid(row=2, padx=20, pady=(0, 20))
        self.safety_circuit_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        safety_frame_title = tk.Label(self.safety_circuit_frame, text="Safety Circuit", font="Helvetica 14 bold")
        safety_frame_title.grid(padx=5, pady=5)
