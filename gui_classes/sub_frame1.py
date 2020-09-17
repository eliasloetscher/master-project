import tkinter as tk


class SubFrame1:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame  # this is the root
        self.sub_frame1 = tk.Frame(parent_frame, width=600, height=600)
        self.sub_frame1.grid_propagate(False)
        self.sub_frame1.grid(row=3, padx=10, columnspan=4, sticky="W")
        self.sub_frame1.grid_forget()
        tk.Label(self.sub_frame1, text="Subframe 1", font="Helvetica 12 bold").grid(row=0, pady=20, columnspan=4,
                                                                                    sticky="W")