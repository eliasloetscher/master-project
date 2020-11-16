import tkinter as tk


class MeasurementFrame:
    """ This class implements the gui widget for the measurement frame.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions):
        """ Constructor of the measurement frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.measurement_frame = tk.Frame(self.master, width=700, height=520, highlightbackground="black",
                                          highlightthickness=1)
        self.measurement_frame.grid(row=1, column=1, padx= (0, 20), pady=(0, 20), rowspan=2)
        self.measurement_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        measurement_frame_title = tk.Label(self.measurement_frame, text="Measurements", font="Helvetica 14 bold")
        measurement_frame_title.grid(padx=5, pady=5)
