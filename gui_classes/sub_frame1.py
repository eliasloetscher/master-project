import tkinter as tk


class SubFrame1:
    def __init__(self, parent_frame, labjack_connection, labjack_gpio):
        # Initialize vars
        self.parent_frame = parent_frame  # this is the root
        self.lj_connection = labjack_connection
        self.lj_gpio = labjack_gpio

        # Setup frame properties
        self.sub_frame1 = tk.Frame(parent_frame, width=600, height=600)
        self.sub_frame1.grid_propagate(False)
        self.sub_frame1.grid(row=3, padx=10, columnspan=4, sticky="W")
        self.sub_frame1.grid_forget()

        # Setup var labels
        self.safety_circuit_state = tk.Label(self.sub_frame1, text="OFF", fg="green")  # changed by switch functions
        self.hv_relay_state = tk.Label(self.sub_frame1, text="OFF", fg="green")  # changed by switch functions
        self.gnd_relay_state = tk.Label(self.sub_frame1, text="OFF", fg="green")  # changed by switch functions
        self.error_message = tk.Label(self.sub_frame1, text="", fg="red")  # changed by switch functions

        # title
        tk.Label(self.sub_frame1, text="Safety circuit", font="Helvetica 12 bold").grid(row=0, pady=20, columnspan=4, sticky="W")


        # Buttons for safety circuit
        tk.Label(self.sub_frame1, text="Safety circuit").grid(row=1, pady=5, columnspan=4, sticky='W')
        tk.Button(self.sub_frame1, text="ON",
                  command=lambda: self.lj_gpio.switch_relay_with_gui_label_change('ON', 'SAFETY', self.safety_circuit_state, self.error_message, self.lj_connection)).grid(row=1, column=1, pady=10, sticky="W")

        tk.Button(self.sub_frame1, text="OFF",
                  command=lambda: self.lj_gpio.switch_relay_with_gui_label_change('OFF', 'SAFETY', self.safety_circuit_state, self.error_message, self.lj_connection)).grid(row=1, column=2, padx=15, sticky="W")

        # Buttons for hv relay
        tk.Label(self.sub_frame1, text="HV relay").grid(row=2, pady=5, columnspan=4, sticky='W')
        tk.Button(self.sub_frame1, text="ON",
                  command=lambda: self.lj_gpio.switch_relay_with_gui_label_change('ON', 'HV', self.hv_relay_state, self.error_message, self.lj_connection)).grid(row=2, column=1, pady=10, sticky="W")
        tk.Button(self.sub_frame1, text="OFF",
                  command=lambda: self.lj_gpio.switch_relay_with_gui_label_change('OFF', 'HV', self.hv_relay_state, self.error_message, self.lj_connection)).grid(row=2, column=2, padx=15, sticky="W")

        # Buttons for GND
        tk.Label(self.sub_frame1, text="GND relay").grid(row=3, pady=5, columnspan=4, sticky='W')
        tk.Button(self.sub_frame1, text="ON",
                  command=lambda: self.lj_gpio.switch_relay_with_gui_label_change('ON', 'GND', self.gnd_relay_state, self.error_message, self.lj_connection)).grid(row=3, column=1, pady=10, sticky="W")
        tk.Button(self.sub_frame1, text="OFF",
                  command=lambda: self.lj_gpio.switch_relay_with_gui_label_change('OFF', 'GND', self.gnd_relay_state, self.error_message, self.lj_connection)).grid(row=3, column=2, padx=15, sticky="W")

        tk.Label(self.sub_frame1, text="Safety circuit: ").grid(row=4, pady=(10, 0), sticky="W")
        tk.Label(self.sub_frame1, text="HV relay: ").grid(row=5, pady=(10, 0), sticky="W")
        tk.Label(self.sub_frame1, text="GND relay: ").grid(row=6, pady=(10, 0), sticky="W")

        self.safety_circuit_state.grid(row=4, columnspan=4, column=1, sticky="W", pady=(0, 0))
        self.hv_relay_state.grid(row=5, columnspan=4, column=1, sticky="W", pady=(0, 0))
        self.gnd_relay_state.grid(row=6, columnspan=4, column=1, sticky="W", pady=(10, 0))

        self.error_message.grid(row=7, columnspan=5, sticky="W", pady=(20, 0))
