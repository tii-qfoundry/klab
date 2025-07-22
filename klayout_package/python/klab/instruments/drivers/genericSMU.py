"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
## Generic SMU Driver
# This driver is a dummy implementation for development purposes.


from ..abstract_classes import SMU
from ..yaml_utils import yaml_method

class GenericSMU(SMU):
    """
    A dummy driver for a generic Source Measure Unit (SMU) for development.
    It uses the SCPIInstrument base class to provide functionality from a YAML file.
    This driver is intended for development and testing when a physical
    instrument is not available.
    """
    def __init__(self, name, address = "TCPIP0::192.168.0.95::INSTR", **kwargs):
        """
        Initializes the DummySMU driver.

        Args:
            name (str): The name of the instrument instance.
            address (str): The VISA address (e.g., 'GPIB0::24::INSTR' or 'DUMMY' for dev).
            **kwargs: Additional keyword arguments passed to the base class.
        """
        super().__init__(name, address, **kwargs)

    @yaml_method
    def source_voltage(self, voltage: float, current_compliance: float): 
        pass
    
    @yaml_method
    def source_current(self, current: float, voltage_compliance: float):
        pass
    
    @yaml_method        
    def measure_voltage(self):
        pass

    @yaml_method  
    def measure_current(self):
        pass

    @yaml_method    
    def enable_source(self, state: bool):
        pass