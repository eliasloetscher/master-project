import tkinter as tk


class ControlFrame:
    """ This class implements the gui widget for the control section.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions):
        """ Constructor of the control frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.control_frame = tk.Frame(self.master, width=500, height=250, highlightbackground="black",
                                      highlightthickness=1)
        self.control_frame.grid(row=3, padx=20, pady=(0, 20))
        self.control_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        control_frame_title = tk.Label(self.control_frame, text="Control", font="Helvetica 14 bold")
        control_frame_title.grid(padx=5, pady=5)
