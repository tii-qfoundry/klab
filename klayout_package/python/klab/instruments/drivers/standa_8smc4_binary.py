"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
## Standa 8SMC4-USB Driver
# Concrete driver for Standa 8SMC4-USB motor controllers. This
# instrument communicates with binary packets, not SCPI. This is an 
# example of how to implement a driver for a specific instrument
# using the base KlabInstrument class, when the instrument does not
# use SCPI commands but instead uses a custom binary protocol.

from ..abstract_classes import MotorStage
from ..klab_instrument import enum_parameter_class

import struct
import time
import collections

# --- Data Structures and Enums ---

StepperCalibration = collections.namedtuple("StepperCalibration", ["steps_per_rev", "usteps_per_step"])

# These enums define the constants used by the Standa controller,
# making the code more readable and preventing errors from magic numbers.
MOTOR_TYPE = enum_parameter_class("MotorType", {"NONE": 0x00, "DC": 0x01, "STEP": 0x03, "BRUSHLESS": 0x05}, default="STEP")
STATE_CMD = enum_parameter_class("StateCmd", {"MOVE": 0x01, "RIGHT": 0x04, "STOP": 0x05, "HOME": 0x06})
DRIVER_TYPE = enum_parameter_class("DriverType",{"FET": 0x01,  "INTEGR": 0x02, },default="FET")
STATE_PWR = enum_parameter_class("PowerState",{"UNKNOWN": 0x00,"OFF": 0x01,"NORM": 0x03,"REDUCT": 0x04,"MAX": 0x05,},default="UNKNOWN")
STATE_ENC = enum_parameter_class("EncoderState",{"ABSENT": 0x00,"UNKNOWN": 0x01,"MALFUNC": 0x02,"REFERSE": 0x03,"OK": 0x04,},default="UNKNOWN")
STATE_WND = enum_parameter_class("WindowState",{"ABSENT": 0x00,"UNKNOWN": 0x01,"MALFUNC": 0x02,"OK": 0x03,},default="UNKNOWN")

# --- Standa 8SMC4 Driver ---

class Standa8SMC4Bin(MotorStage):
    """
    Driver for Standa 8SMC4-USB motor controllers.
    """
    _COMMANDS = {
        # command_name: (request_format, response_format, response_length_bytes)
        "gpos": (None, "<i", 4),
        "gets": (None, "<i", 4), # Simplified for just position, a full status is more complex
        "move": ("<i", None, 0),
        "movr": ("<i", None, 0),
        "stop": (None, None, 0),
        "sels": ("<i", None, 0), # Set speed
        "geng": (None, "<II", 8), # Get motor settings
        "gent": (None, "<B", 1), # Get motor type
    }

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, **kwargs)
        if self._visa_instrument:
            # Standa devices require specific termination characters
            self._visa_instrument.read_termination = ''
            self._visa_instrument.write_termination = ''
            print(f"Standa 8SMC4 Driver: Initialized {self.name}.")

    def _execute(self, command_name: str, *args):
        """
        A unified method to pack, send, receive, and unpack binary commands.
        """
        if self._visa_instrument is None:
            print(f"Cannot execute '{command_name}': Instrument not connected.")
            return None

        if command_name not in self._COMMANDS:
            raise ValueError(f"Command '{command_name}' is not defined for this driver.")

        req_fmt, resp_fmt, resp_len = self._COMMANDS[command_name]

        # Pack the command and arguments into a binary string
        if req_fmt:
            # Command name (4 bytes) + packed arguments
            message = command_name.encode('ascii') + struct.pack(req_fmt, *args)
        else:
            # Just the command name
            message = command_name.encode('ascii')

        # Send the command
        self._visa_instrument.write_raw(message)
        
        # Read and unpack the response if one is expected
        if resp_len > 0 and resp_fmt:
            response_bytes = self._visa_instrument.read_bytes(resp_len)
            response_tuple = struct.unpack(resp_fmt, response_bytes)
            # If the response is a single item, return it directly, otherwise return the tuple
            return response_tuple[0] if len(response_tuple) == 1 else response_tuple
        
        return None

    # --- Implementation of abstract MotorStage methods ---

    def get_position(self, axis: int = 0) -> int:
        """Gets the current position of an axis in microsteps."""
        # The 'gpos' command actually returns position, uPosition, and encoder position.
        # We simplify here and just use 'gets' which returns the position as a simple int.
        return self._execute("gets") or 0

    def move_to(self, position: int, axis: int = 0):
        """Moves an axis to an absolute position in microsteps."""
        self._execute("move", int(position))

    def move_by(self, distance: int, axis: int = 0):
        """Moves an axis by a relative distance in microsteps."""
        self._execute("movr", int(distance))

    def set_speed(self, speed: int, axis: int = 0):
        """Sets the movement speed in microsteps/sec."""
        self._execute("sels", int(speed))
        
    def stop(self, axis: int = 0):
        """Stops the movement of an axis immediately."""
        self._execute("stop")

    # --- Instrument-specific helper methods ---

    def get_stepper_calibration(self, axis: int = 0) -> StepperCalibration:
        """Gets the stepper motor calibration data."""
        response = self._execute("geng")
        if response:
            return StepperCalibration._make(response)
        return StepperCalibration(0, 0)

    def get_motor_type(self, axis: int = 0) -> MOTOR_TYPE:
        """Gets the type of motor for the specified axis."""
        response = self._execute("gent")
        if response:
            return MOTOR_TYPE(response)
        return MOTOR_TYPE.NONE

