"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

# ===================================================================
# This file defines the abstract base class for Vector Network Analyzers (VNA).
# ===================================================================

from abc import ABC, abstractmethod
from ..scpi_instrument import ScpiInstrument


class VNA(ScpiInstrument, ABC):
    """
    Abstract base class for Vector Network Analyzer (VNA) instruments.

    This class defines a standardized interface for VNA devices, ensuring
    consistent operation across different models. It inherits from

    `ScpiInstrument` and outlines the essential methods required for
    VNA measurements.
    """

    @abstractmethod
    def setup_sweep(self, start_freq: float, stop_freq: float, num_points: int):
        """
        Configure the VNA for a frequency sweep.

        Args:
            start_freq (float): The starting frequency of the sweep, in Hz.
            stop_freq (float): The stopping frequency of the sweep, in Hz.
            num_points (int): The number of points to measure in the sweep.
        """
        pass
    
    @abstractmethod
    def measure_s_parameters(self, ports: tuple = (1, 2)) -> dict:
        """
        Perform an S-parameter measurement.

        Args:
            ports (tuple, optional): A tuple indicating the S-parameter to
                                   measure (e.g., (1, 1) for S11, (2, 1) for S21).
                                   Defaults to (1, 2).

        Returns:
            dict: A dictionary containing the measured S-parameter data,
                  typically including frequency and complex data points.
        """
        pass
