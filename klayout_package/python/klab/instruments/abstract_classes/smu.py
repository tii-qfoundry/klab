"""
klab - A Python package for KLayout integration with lab instrumentation.


Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

# ===================================================================
# This file defines the abstract base class for Source-Measure Units (SMU).
# ===================================================================

from abc import ABC, abstractmethod
from ..scpi_instrument import ScpiInstrument


class SMU(ScpiInstrument, ABC):
    """Abstract Source-Measure Unit base class."""
    
    @abstractmethod
    def source_voltage(self, voltage: float, current_compliance: float): 
        """Set the SMU to source voltage mode with specified compliance.
        
        Args:
            voltage: The voltage level to source (in Volts)
            current_compliance: The current compliance limit (in Amperes)
        """
        pass
        
    @abstractmethod
    def source_current(self, current: float, voltage_compliance: float):
        """Set the SMU to source current mode with specified compliance.
        
        Args:
            current: The current level to source (in Amperes)
            voltage_compliance: The voltage compliance limit (in Volts)
        """
        pass
    
    @abstractmethod
    def measure_voltage(self):
        """Measure voltage from the SMU.
        
        Returns:
            float: The measured voltage value (in Volts)
        """
        pass
        
    @abstractmethod
    def measure_current(self):
        """Measure current from the SMU.
        
        Returns:
            float: The measured current value (in Amperes)
        """
        pass
        
    @abstractmethod
    def enable_source(self, state: bool):
        """Enable or disable the source output.
        
        Args:
            state: True to enable output, False to disable
        """
        pass
