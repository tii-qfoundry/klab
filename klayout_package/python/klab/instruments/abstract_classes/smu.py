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
    """
    Abstract base class for Source-Measure Unit (SMU) instruments.

    This class defines a standardized interface for SMU devices, ensuring
    that different SMU models can be used interchangeably. It inherits from
    `ScpiInstrument` and requires subclasses to implement fundamental SMU
    operations.
    """

    @abstractmethod
    def source_voltage(self, voltage: float, current_compliance: float):
        """
        Configure the SMU to source a specific voltage.

        Args:
            voltage (float): The voltage level to source, in volts.
            current_compliance (float): The maximum current the SMU can provide
                                      before entering compliance, in amperes.
        """
        pass
        
    @abstractmethod
    def source_current(self, current: float, voltage_compliance: float):
        """
        Configure the SMU to source a specific current.

        Args:
            current (float): The current level to source, in amperes.
            voltage_compliance (float): The maximum voltage the SMU can provide
                                      before entering compliance, in volts.
        """
        pass
    
    @abstractmethod
    def measure_voltage(self, **kwargs) -> float:
        """
        Perform a voltage measurement.

        Args:
            **kwargs: Additional parameters for the measurement, such as
                      `current` for 4-wire measurements.

        Returns:
            float: The measured voltage in volts.
        """
        pass
        
    @abstractmethod
    def measure_current(self, **kwargs) -> float:
        """
        Perform a current measurement.

        Args:
            **kwargs: Additional parameters for the measurement, such as
                      `voltage` to apply during the measurement.

        Returns:
            float: The measured current in amperes.
        """
        pass
        
    @abstractmethod
    def enable_source(self, state: bool):
        """
        Enable or disable the instrument's output source.

        Args:
            state (bool): True to enable the source, False to disable it.
        """
        pass
