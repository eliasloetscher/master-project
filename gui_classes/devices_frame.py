import tkinter as tk


class DevicesFrame:
    """ This class implements the gui widget for the device connection.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions):
        """ Constructor of the device frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.devices_frame = tk.Frame(self.master, width=500, height=200, highlightbackground="black",
                                      highlightthickness=1)
        self.devices_frame.grid(row=1, padx=20, pady=(0, 20))
        self.devices_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        devices_frame_title = tk.Label(self.devices_frame, text="Devices", font="Helvetica 14 bold")
        devices_frame_title.grid(padx=5, pady=5)
