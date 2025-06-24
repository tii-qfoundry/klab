"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

import pya

try:
    # This will only work when run from within KLayout's environment
    from klab.instruments import Keithley2450
except ImportError:
    # If run outside KLayout, we can't import the driver, but the PCell can still be defined.
    print("Warning: Could not import klab drivers. PCell will load but measurement will fail.")
    SMU = None

class ResistanceMeasurement(pya.PCellDeclarationHelper):
    """
    A KLayout PCell that connects to a Keithley SMU to perform a resistance measurement
    and displays the result as text in the layout.
    """
    visa_address = "TCPIP0::192.168.0.95::INSTR"
    
    def __init__(self):
        super(ResistanceMeasurement, self).__init__()

        # --- PCell Parameters ---
        self.param("ip_address", pya.PCellParameterDeclaration.TypeString, "Instrument IP Address", default="192.168.0.95")
        self.param("value", pya.PCellParameterDeclaration.TypeString, "Measured Resistance", default="Not measured", readonly=True)

        # Define a layer for the text label
        self.param("layer", self.TypeLayer, "Layer", default=pya.LayerInfo(68, 0))
         

    def display_text_impl(self):
        # This method is called by KLayout to generate the PCell's display name
        return f"ResistanceMeasurementCell (R: {self.value})"

    def coerce_parameters_impl(self):
        self.visa_address = f"TCPIP0::{self.ip_address}::INSTR"
        print(f"Coercing parameters: IP Address set to {self.visa_address}")
        # This method is called when a parameter is changed. We use it to trigger the measurement.
        
        
    def produce_impl(self):
        # This method generates the actual layout geometry.
        text_size_microns = 0.2
        # --- 1. Create the center marker ---
        # Get the database unit (dbu) from the layout to convert microns to database units.
        dbu = self.layout.dbu
        
        # Define the size of the marker in microns.
        marker_size_microns = 10.0
        
        # Calculate half the size in database units.
        half_size_dbu = (marker_size_microns / 2.0) / dbu
        
        # Create a pya.Box object centered at the origin (0,0).
        marker_box = pya.Box(-half_size_dbu, -half_size_dbu, half_size_dbu, half_size_dbu)
        
        # Insert the box onto the specified layer.
        self.cell.shapes(self.layer_layer).insert(marker_box)
        
        # --- 2. Create the text label ---
        text_to_display = f"R = {self.value}"
        
        # Create a text object. We'll place it slightly above the marker for better visibility.
        text_y_offset = (marker_size_microns / 2.0 - 2*text_size_microns) / dbu # Place text 0.1um above the box
        text_x_offset = (-marker_size_microns/ 2.0 + text_size_microns)/dbu 
        text:pya.Text = pya.Text(text_to_display, pya.Trans(pya.Trans.R0, text_x_offset, text_y_offset))
        # Set the text size and font. Adjust as needed.
        text.size = text_size_microns/dbu 
        
        # Insert the text onto the same layer.
        self.cell.shapes(self.layer_layer).insert(text)
        

    def _run_measurement(self):
        """Connects to the SMU, performs the measurement, and updates the parameter."""
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
            # These parameters can also be exposed in the PCell if needed
            response = smu.meas_resistance(current=1e-5, voltage_compliance=0.1, count=2)
        
            if isinstance(response, list) and all(isinstance(item, list) for item in response):
                # Flatten the list of lists
                response = [item for sublist in response for item in sublist]
            # Now we can check if the response is a list or a single value
            resistance = response[0] if isinstance(response, list) else response
            
            if isinstance(resistance, str):
                try:
                    resistance = eval(resistance)  # Convert string representation to list
                except Exception as e:
                    print(f"Error converting resistance string to list: {e}")
                    self.value = "Measurement Error"
                    return
                if isinstance(resistance, (list, tuple)) and len(resistance) > 1:
                    # Extract the resistance values from the list, assuming they are in pairs of [voltage, resistance]
                    resistance_values = [resistance[i + 1] for i in range(0, len(resistance), 2)]
                    # Calculate the average resistance
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
