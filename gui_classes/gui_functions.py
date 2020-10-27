from mviss_module.parameters import Parameters as Params


class GUIFunctions:

    def __init__(self, sub_frame1, sub_frame2, sub_frame3):
        self.sub_frame1 = sub_frame1
        self.sub_frame2 = sub_frame2
        self.sub_frame3 = sub_frame3
        self.debug = Params.DEBUG

    def show_sub_frame1(self):
        self.sub_frame1.grid(row=4, padx=10, columnspan=4, sticky="W")
        self.sub_frame2.grid_forget()
        self.sub_frame3.grid_forget()

    def show_sub_frame2(self):
        self.sub_frame1.grid_forget()
        self.sub_frame2.grid(row=4, padx=10, columnspan=4, sticky="W")
        self.sub_frame3.grid_forget()

    def show_sub_frame3(self):
        self.sub_frame1.grid_forget()
        self.sub_frame2.grid_forget()
        self.sub_frame3.grid(row=4, padx=10, columnspan=4, sticky="W")