"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
## Standa 8SMC4 Motor Stage Driver using libximc
# This module provides a custom communication backend for XIMC devices
# using the libximc library, specifically for the Standa 8SMC4 motor stage.

import os
import pathlib

import libximc.highlevel as ximc

from ..abstract_classes import MotorStage
from ..comm import CommBackend

class XimcBackend(CommBackend):
    """Communication backend for XIMC (libximc) devices."""
    
    def __init__(self):
        self._axis = None
        self._device_uri = None
    
    def connect(self, address: str) -> bool:
        """Establish connection to XIMC device."""
        try:
            # Handle different address formats
            if address.startswith("xi-"):
                self._device_uri = address
            elif address.endswith(".bin"):
                # Virtual device file
                self._device_uri = f"xi-emu:///{address}"
            elif ":" in address and not address.startswith("xi-"):
                # Assume TCP format like "192.168.1.100:1820"
                self._device_uri = f"xi-tcp://{address}"
            else:
                # Try as-is or add TCP prefix
                self._device_uri = f"xi-tcp://{address}"
            
            if not ximc.is_valid_address(self._device_uri):
                print(f"Invalid XIMC address format: {self._device_uri}")
                return False
            
            self._axis = ximc.Axis(self._device_uri)
            self._axis.open_device()
            return True
            
        except Exception as e:
            print(f"XIMC connection failed: {e}")
            self._axis = None
            return False
    
    def disconnect(self):
        """Close the XIMC connection."""
        if self._axis:
            try:
                self._axis.close_device()
            except Exception as e:
                print(f"Error closing XIMC device: {e}")
            finally:
                self._axis = None
    
    def write(self, command: str):
        """XIMC devices don't use text commands - this is a no-op."""
        pass
    
    def read(self) -> str:
        """XIMC devices don't return text responses - this is a no-op."""
        return ""
    
    def query(self, command: str) -> str:
        """XIMC devices don't use text queries - this is a no-op."""
        return ""
    
    def is_connected(self) -> bool:
        """Check if XIMC device is connected."""
        return self._axis is not None
    
    def get_axis(self):
        """Get the underlying XIMC Axis object for direct access."""
        return self._axis


class Standa8SMC4(MotorStage):
    """
    Klab driver for the Standa 8SMC4 motor stage, using the libximc library.
    
    This class uses a custom XimcBackend for communication instead of VISA.
    """

    def __init__(self, name: str, address: str, **kwargs):
        # Create custom communication backend
        ximc_backend = XimcBackend()
        
        # Initialize with custom backend (no VISA)
        super().__init__(name, address, communication_backend=ximc_backend, **kwargs)
        
        if not address:
            raise ValueError("Address must be provided for Standa 8SMC4 device.")
    
    @property
    def axis(self):
        """Get the underlying XIMC Axis object for direct access."""
        return self._comm_backend.get_axis()
    
    def get_position(self, axis: int = 0) -> float:
        """Get the current position of the motor stage."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        position = self.axis.get_position()
        return float(position.Position)
    
    def move_to(self, position: float, axis: int = 0):
        """Move to an absolute position."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        self.axis.command_move(int(position), 0)
    
    def move_by(self, distance: float, axis: int = 0):
        """Move by a relative distance."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        current_pos = self.get_position(axis)
        target_pos = current_pos + distance
        self.move_to(target_pos, axis)
    
    
    def stop(self, axis: int = 0):
        """Stop the motor movement."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        self.axis.command_stop()
    
    def home(self, axis: int = 0):
        """Home the motor stage."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        self.axis.command_home()
    
    def command_zero(self):
        """Set current position as zero reference."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        self.axis.command_zero()
    
    def get_status(self):
        """Get the current status of the motor."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        return self.axis.get_status()
    
    def is_moving(self) -> bool:
        """Check if the motor is currently moving."""
        if not self.is_connected():
            return False
        
        status = self.get_status()
        return bool(status.MvCmdSts & ximc.MvcmdStatus.MVCMD_RUNNING)
    
    def set_move_settings(self, speed: float = None, acceleration: float = None):
        """Set the move settings for the motor stage."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        
        # Example: Set speed and acceleration
        move_settings = self.axis.get_move_settings()
        if speed is not None:
            move_settings.Speed = int(speed)
        if acceleration is not None:
            move_settings.Acceleration = int(acceleration)
        self.axis.set_move_settings(move_settings)
    
    def set_speed(self, speed: float = None):
        """Set the speed for the motor stage."""
        self.set_move_settings(speed=speed)
                               
    def set_acceleration(self, acceleration: float = None):
        """Set the acceleration for the motor stage."""
        self.set_move_settings(acceleration=acceleration)

    

if __name__ == "__main__":
    # Example usage
    try:
        # Test with virtual device file
        virtual_device_file = os.path.join(os.getcwd(), "virtual_motor_controller.bin")
        stage = Standa8SMC4(name="Standa Stage", address=virtual_device_file)
        
        if stage.is_connected():
            print(f"Current position: {stage.get_position()}")
            stage.move_to(1000)
            print("Moving to position 1000...")
            
            # Wait for movement to complete
            import time
            while stage.is_moving():
                print(f"Position: {stage.get_position()}")
                time.sleep(0.1)
            
            print(f"Final position: {stage.get_position()}")
            stage.disconnect()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e