import tkinter as tk


class RecordingFrame:
    """ This class implements the gui widget for recording section.

    Methods
    ---------
    None
    """

    def __init__(self, master, gui_functions):
        """ Constructor of the recording frame class

        :param master: parent frame/window
        :param gui_functions: instance of gui_functions used to handle all gui actions
        """

        # Initialize vars
        self.master = master
        self.gui_functions = gui_functions

        # Initialize and place frame
        self.recording_frame = tk.Frame(self.master, width=650, height=150, highlightbackground="black",
                                             highlightthickness=1)
        self.recording_frame.grid(row=4, column=1, padx=(0, 20), pady=(0, 20))
        self.recording_frame.grid_propagate(False)  # Avoid frame shrinking to the size of the included elements

        # Set and place frame title
        recording_frame_title = tk.Label(self.recording_frame, text="Recordings", font="Helvetica 14 bold")
        recording_frame_title.grid(padx=5, pady=5)
