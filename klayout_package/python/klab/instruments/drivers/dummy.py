"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
from klab.instrument import SMU
import random

class Dummy(SMU):
    """
    A dummy driver for a generic Source Measure Unit (SMU) for development.
    It uses the SCPIInstrument base class to provide functionality from a YAML file.
    This driver is intended for development and testing when a physical
    instrument is not available.
    """
    def __init__(self, name, address = "TCP", **kwargs):
        """
        Initializes the DummySMU driver.

        Args:
            name (str): The name of the instrument instance.
            address (str): The VISA address (e.g., 'GPIB0::24::INSTR' or 'DUMMY' for dev).
            **kwargs: Additional keyword arguments passed to the base class.
        """
        super().__init__(name, address, **kwargs)

    def source_voltage(self, voltage: float, current_compliance: float): 
        print("DummySMU: source_voltage called with voltage =", voltage, "and compliance =", current_compliance)
        return
        
    def source_current(self, current: float, voltage_compliance: float):
        print("DummySMU: source_current called with current =", current, "and compliance =", voltage_compliance)
        return
    
    def measure_voltage(self):
        print("DummySMU: measure_voltage called")
        return random.uniform(0, 1)
        
    def measure_current(self):
        print("DummySMU: measure_current called")
        return random.uniform(0, 1)
        
    def enable_source(self, state: bool):
        print("DummySMU: enable_source called with state =", state)
        return state