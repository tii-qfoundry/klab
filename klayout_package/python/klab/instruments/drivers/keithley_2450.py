"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
## Keithley 2450 SMU Driver
# This driver provides a high-level interface for controlling the Keithley 2450 SMU.
# It demonstrates how to use both explicit Python methods and dynamic SCPI commands
# to interact with the instrument. The driver is designed to be flexible and extensible,
# allowing for easy addition of new methods via a YAML configuration file.
#
# Ways of defining and calling methods:
#   1. Explicitly in Python (e.g., set_average_count).
#   2. Dynamically from a YAML file (e.g., enable_source, if defined).
#   3. On-the-fly via the SCPI proxy (e.g., self.source.function('VOLT')).


# Add klab to path if not already present
from ..abstract_classes import SMU
from ..yaml_utils import yaml_method
from ..scpi_instrument import NoQuote
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
    # Their implementation uses the dynamic SCPI proxy. They can send
    # structured commands to the instrument, which are not defined in the driver
    # but are constructed on-the-fly. When using abstract classes like SMU, abstract 
    # methods need to be defined in the driver class, even if they are explicitly 
    # implemented in the YAML file. The yaml dricers are availabl in klayout_package/tech


    # Use this decorator to indicate that this method is defined in the YAML driver file.
    @yaml_method 
    def source_voltage(self, voltage: float, current_compliance: float):
        """Set the SMU to source voltage mode with specified compliance.
        Implemented in YAML."""
        pass
    
    @yaml_method
    def source_current(self, current: float, voltage_compliance: float=0.1):
        """Configures the instrument to source a specific current."""
        pass

    # Yaml implememted methods can be invoqued from other methods.
    def measure_voltage(self, current = 1e-3) -> float:
        """Measures voltage. """
        self.source_current(current =current)
        return self.read_measurement()
    
    def measure_current(self, voltage = 1e-3) -> float:
        """Measures current using the instrument's YAML method specification."""
        self.source_voltage(voltage = voltage)
        return self.read_measurement()
    
    # Use dymaic SCPI commands: the method 'output' is not defined in the YAML file, 
    # but falls back to use the dynamic SCPI proxy. Text passed to some methods needs
    # to be wrapped in NoQuote() to avoid adding quotes around it. This depends on the
    # SCPI command syntax for your instrument.

    def enable_source(self, enable:bool = True):
        return self.output(NoQuote('ON') if enable else NoQuote('OFF'))
    
    # Alternatively, methods specified in the YAML can be called dynamically.
    def source_resistance(self, current: float = 1e-6, voltage_compliance: float = 1e-3):
        """Sets the instrument to source voltage by calling the YAML method."""
        self._execute_yaml_method('set_resistance', current=current, vlim=voltage_compliance)


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
        getattr(self.sense, func).average.count(count)
        getattr(self.sense, func).average.state('ON')
        #self.sense[func].average.state('ON')
        print(f"Set averaging for {func} to {count} readings.")

    # Or directly query SCPI commands
    def reset(self):
        """Resets the instrument to its default state."""
        self.write("*RST")
        print("Instrument reset to default state.")


if __name__ == "__main__":
    # Example usage of the Keithley2450 driver
    # Replace with your instrument's actual VISA address
    VISA_ADDRESS = 'TCPIP0::192.168.0.95::INSTR'
    
    try:
        smu = Keithley2450(name='Keithley 2450', address=VISA_ADDRESS)
        if smu._visa_instrument:
            methods = smu.get_available_methods()
            res = smu.meas_resistance(current=1e-3, voltage_compliance=0.1, count=10)  # Set current with compliance
            print(f"Measure resistance: {res} Ohms")
            smu.disconnect()  # Close the connection when done
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
