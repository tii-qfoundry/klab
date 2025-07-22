"""
ResistanceMeasurement PCell for Klab
=======================================

This module defines a Klab PCell that connects to a Keithley SMU to perform a resistance measurement
and displays the result as text in the layout. It is designed to be used within the Klab environment.

Features:
- Connects to a Keithley 2450 SMU using the klab instrument driver
- Performs a resistance measurement and displays the result in the layout

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.
"""

try:
    import pya
except ImportError:
    import klayout.db as pya

from klab.instruments import Keithley2450

class ResistanceMeasurement(pya.PCellDeclarationHelper):
    """
    KLayout PCell for automated resistance measurement using a Keithley SMU.

    This PCell connects to a Keithley 2450 SMU, performs a resistance measurement,
    and displays the measured value as text in the layout. It is intended for use
    in lab automation and rapid prototyping of measurement cells in KLayout.

    Parameters:
        ip_address (str): IP address of the instrument
        value (str): Measured resistance (read-only)
        layer (LayerInfo): Layer for the text label
    """
    visa_address = "TCPIP0::192.168.0.95::INSTR"
    
    def __init__(self):
        """
        Initializes the PCell and its parameters.
        """
        super(ResistanceMeasurement, self).__init__()

        # --- PCell Parameters ---
        self.param("ip_address", pya.PCellParameterDeclaration.TypeString, "Instrument IP Address", default="192.168.0.95")
        self.param("value", pya.PCellParameterDeclaration.TypeString, "Measured Resistance", default="Not measured", readonly=True)

        # Define a layer for the text label
        self.param("layer", self.TypeLayer, "Layer", default=pya.LayerInfo(68, 0))

    def display_text_impl(self):
        """
        Returns the display name for the PCell in KLayout.
        """
        return f"ResistanceMeasurementCell (R: {self.value})"

    def coerce_parameters_impl(self):
        """
        Called when PCell parameters are changed. Updates the VISA address and can trigger measurement.
        """
        self.visa_address = f"TCPIP0::{self.ip_address}::INSTR"
        print(f"Coercing parameters: IP Address set to {self.visa_address}")
    def produce_impl(self):
        """
        Generates the layout geometry for the PCell, including a marker and a text label
        showing the measured resistance value.
        """
        text_size_microns = 0.2
        # --- 1. Create the center marker ---
        dbu = self.layout.dbu
        marker_size_microns = 10.0
        half_size_dbu = (marker_size_microns / 2.0) / dbu
        marker_box = pya.Box(-half_size_dbu, -half_size_dbu, half_size_dbu, half_size_dbu)
        self.cell.shapes(self.layer_layer).insert(marker_box)

        # --- 2. Create the text label ---
        text_to_display = f"R = {self.value}"
        text_y_offset = (marker_size_microns / 2.0 - 2*text_size_microns) / dbu # Place text 0.1um above the box
        text_x_offset = (-marker_size_microns/ 2.0 + text_size_microns)/dbu 
        text:pya.Text = pya.Text(text_to_display, pya.Trans(pya.Trans.R0, text_x_offset, text_y_offset))
        text.size = text_size_microns/dbu 
        self.cell.shapes(self.layer_layer).insert(text)

    def _run_measurement(self):
        """
        Connects to the Keithley SMU, performs the resistance measurement, and updates the value parameter.

        Handles connection errors, measurement errors, and result formatting.
        """
        if Keithley2450 is None:
            self.value = "Error: klab driver not found."
            return

        self.visa_address = f"TCPIP0::{self.ip_address}::INSTR"
        self.value = "Measuring..."
        try:
            print(f"Connecting to SMU at {self.visa_address}...")
            smu = Keithley2450(name='pcell_smu', address=self.visa_address)

            if not smu.is_connected():
                self.value = "Connection Failed"
                print("Error: Could not connect to the instrument.")
                return

            # Use the high-level measurement method from the driver
            response = smu.meas_resistance(current=1e-5, voltage_compliance=0.1, count=2)
            if isinstance(response, list) and all(isinstance(item, list) for item in response):
                response = [item for sublist in response for item in sublist]
            resistance = response[0] if isinstance(response, list) else response

            if isinstance(resistance, str):
                try:
                    resistance = eval(resistance)  # Convert string representation to list
                except Exception as e:
                    print(f"Error converting resistance string to list: {e}")
                    self.value = "Measurement Error"
                    return
                if isinstance(resistance, (list, tuple)) and len(resistance) > 1:
                    resistance_values = [resistance[i + 1] for i in range(0, len(resistance), 2)]
                    _avg = sum(resistance_values) / len(resistance_values)
                else:
                    _avg = resistance[0] if resistance else 0
                self.value = f"{_avg:.3f}"
            else:
                self.value = str(resistance)

            print(f"Measurement complete. Resistance: {self.value}")
            smu.close()

        except Exception as e:
            self.value = "Measurement Error"
            print(f"An error occurred during measurement: {e}")
