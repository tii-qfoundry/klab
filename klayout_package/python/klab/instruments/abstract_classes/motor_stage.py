"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

# ===================================================================
# This file defines the abstract base class for Motorized Stages.
# ===================================================================

from abc import ABC, abstractmethod
from ..klab_instrument import KlabInstrument


class MotorStage(KlabInstrument, ABC):
    """
    Abstract base class for motor stage controllers.

    This class provides a standard interface for controlling motorized stages,
    abstracting away the specifics of the underlying hardware. It inherits
    from `KlabInstrument` to leverage its communication backend system,
    allowing for drivers that use VISA, serial, or custom protocols.
    """

    @abstractmethod
    def get_position(self, axis: int = 0) -> float:
        """
        Retrieves the current position of the specified axis.

        Args:
            axis (int, optional): The axis to query. Defaults to 0.

        Returns:
            float: The current position in device-specific units (e.g., steps, mm).
        """
        raise NotImplementedError

    @abstractmethod
    def move_to(self, position: float, axis: int = 0):
        """
        Moves the specified axis to an absolute position.

        Args:
            position (float): The target absolute position.
            axis (int, optional): The axis to move. Defaults to 0.
        """
        raise NotImplementedError

    @abstractmethod
    def move_by(self, distance: float, axis: int = 0):
        """
        Moves the specified axis by a relative distance.

        Args:
            distance (float): The relative distance to move.
            axis (int, optional): The axis to move. Defaults to 0.
        """
        raise NotImplementedError

    @abstractmethod
    def set_speed(self, speed: float, axis: int = 0):
        """
        Sets the movement speed for the specified axis.

        Args:
            speed (float): The desired speed in device-specific units.
            axis (int, optional): The axis to configure. Defaults to 0.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self, axis: int = 0):
        """
        Stops any ongoing movement on the specified axis immediately.

        Args:
            axis (int, optional): The axis to stop. Defaults to 0.
        """
        raise NotImplementedError

    @abstractmethod
    def home(self, axis: int = 0):
        """
        Initiates the homing sequence for the specified axis.

        Args:
            axis (int, optional): The axis to home. Defaults to 0.
        """
        raise NotImplementedError
