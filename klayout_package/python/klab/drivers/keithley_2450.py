# ==================================================================
# A hybrid driver for the Keithley 2450 SMU, demonstrating three
# ways of defining and calling methods:
#   1. Explicitly in Python (e.g., set_average_count).
#   2. Dynamically from a YAML file (e.g., enable_source, if defined).
#   3. On-the-fly via the SCPI proxy (e.g., self.source.function('VOLT')).
# ==================================================================

from klab.instrument import SMU
import time

class Keithley2450(SMU):
    """
    Klab driver for the Keithley 2450 SMU.
    
    This class provides high-level methods for common SMU operations
    which are implemented using the dynamic SCPI command builder from the
    parent SCPIInstrument class.
    """
    def __init__(self, name, address, **kwargs):
        # Initialize the parent SMU class. We can optionally point to a YAML
        # file here if we want to define additional high-level methods there.
        super().__init__(name, address, yaml_file='keithley_2450.yml', **kwargs)
        
        if self._visa_instrument:
            # The 'initialize' method is dynamically called from the YAML file.
            self.initialize()

    # --- Explicitly Defined High-Level Methods ---
    # These methods provide a clean, user-friendly interface.
    # Their implementation uses the dynamic SCPI proxy. They send
    # structured commands to the instrument, which are not defined in the driver
    # but are constructed on-the-fly.

    # Methods can directly implement on the fly SCPI commands
    def source_voltage(self, voltage: float, current_compliance: float):
        """Configures the instrument to source a specific voltage."""
        self.source.function('VOLT')
        self.source.voltage(voltage)
        self.source.voltage.ilimit(current_compliance)
    
    # Alternatively, methods can be specified in a YAML file and called dynamically.
    def set_current(self, current: float = 1e-6, voltage_compliance: float = 1e-3):
        """Sets the instrument to source voltage by calling the YAML method."""
        self._execute_yaml_method('source_current', current=current, voltage_compliance=voltage_compliance)

    def get_voltage(self, nplc:int =1) -> float:
        """Measures voltage using the instrument's YAML method specification."""
        self.setup_measure_voltage(nplc=nplc)
        return self.measure_voltage(nplc=nplc)


    # Complex methods can still be defined in the driver specification and themselves use
    # the dynamic SCPI proxy for their implementation.
    def set_average_count(self, function: str, count: int):
        """
        Sets the averaging count for a specific measurement function.

        Args:
            function (str): The measurement function ('VOLT', 'CURR', 'RES').
            count (int): The number of readings to average (1 to 100).
        """
        func = function.upper()
        if func not in ('VOLT', 'CURR', 'RES'):
            raise ValueError("Function must be one of 'VOLT', 'CURR', or 'RES'")
        
        # This method uses the dynamic proxy for its implementation.
        self.sense[func].average.count(count)
        self.sense[func].average.state('ON')
        print(f"Set averaging for {func} to {count} readings.")

    # Or directly inque SCPI commands
    def reset(self):
        """Resets the instrument to its default state."""
        self.write("*RST")
        print("Instrument reset to default state.")
        
