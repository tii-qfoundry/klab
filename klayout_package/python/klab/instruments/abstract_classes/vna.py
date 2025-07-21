"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

# ===================================================================
# This file defines the abstract base class for Vector Network Analyzers (VNA).
# ===================================================================

from abc import ABC, abstractmethod
from ..scpi_instrument import ScpiInstrument


class VNA(ScpiInstrument, ABC):
    """Abstract Vector Network Analyzer base class."""
    
    @abstractmethod
    def setup_sweep(self, start_freq: float, stop_freq: float, num_points: int):
        """Configure the frequency sweep parameters.
        
        Args:
            start_freq: The start frequency for the sweep (in Hz)
            stop_freq: The stop frequency for the sweep (in Hz)  
            num_points: The number of measurement points in the sweep
        """
        pass
    
    @abstractmethod
    def measure_s_parameters(self):
        """Measure S-parameters.
        
        Returns:
            The measured S-parameter data (format depends on implementation)
        """
        pass
