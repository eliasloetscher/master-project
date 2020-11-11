import tkinter as tk


class SubFrame3:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame  # this is the root
        self.sub_frame3 = tk.Frame(parent_frame, width=700, height=800)
        self.sub_frame3.grid_propagate(False)
        self.sub_frame3.grid(row=3, padx=10, columnspan=4, sticky="W")
        self.sub_frame3.grid_forget()
        tk.Label(self.sub_frame3, text="Subframe 3", font="Helvetica 12 bold").grid(row=0, pady=20, columnspan=4,
                                                                                    sticky="W")