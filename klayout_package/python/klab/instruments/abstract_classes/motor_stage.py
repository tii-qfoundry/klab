"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

# ===================================================================
# This file defines the abstract base class for Motorized Stages.
# ===================================================================

from abc import ABC, abstractmethod
from ..klab_instrument import KlabInstrument


class MotorStage(KlabInstrument, ABC):
    """Abstract Base Class for a Motorized Stage.
    
    This class defines the interface for controlling motorized positioning stages.
    It inherits from KlabInstrument to support various communication backends.
    """
    
    @abstractmethod
    def get_position(self, axis: int = 0) -> float:
        """Get the current position of the specified axis.
        
        Args:
            axis: The axis number (default: 0)
            
        Returns:
            float: The current position in device units
        """
        raise NotImplementedError
    
    @abstractmethod
    def move_to(self, position: float, axis: int = 0):
        """Move to an absolute position.
        
        Args:
            position: The target position in device units
            axis: The axis number (default: 0)
        """
        raise NotImplementedError
    
    @abstractmethod
    def move_by(self, distance: float, axis: int = 0):
        """Move by a relative distance.
        
        Args:
            distance: The distance to move in device units
            axis: The axis number (default: 0)
        """
        raise NotImplementedError
    
    @abstractmethod
    def set_speed(self, speed: float, axis: int = 0):
        """Set the movement speed for the specified axis.
        
        Args:
            speed: The movement speed in device units per second
            axis: The axis number (default: 0)
        """
        raise NotImplementedError
    
    @abstractmethod
    def stop(self, axis: int = 0):
        """Stop movement on the specified axis.
        
        Args:
            axis: The axis number (default: 0)
        """
        raise NotImplementedError
    
    @abstractmethod
    def home(self, axis: int = 0):
        """Home the specified axis to its reference position.
        
        Args:
            axis: The axis number (default: 0)
        """
        raise NotImplementedError
