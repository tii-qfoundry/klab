"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
# ==================================================================
# This file defines the core architecture for instruments, featuring
# a base class for VISA communication and a specialized SCPI class
# with a dynamic proxy for on-the-fly command generation.
# ==================================================================

import pyvisa as visa
import time
import yaml
import os
import struct
from abc import ABC, abstractmethod
from typing import Tuple, List, Union

class _QueryMarker: pass
q = _QueryMarker()

class NoQuote:
    """
    A wrapper class to indicate that a string argument should not be
    enclosed in quotation marks when sent in a SCPI command.
    
    Example:
        smu.source.function(NoQuote('VOLT')) # Sends: :SOUR:FUNC VOLT
    """
    def __init__(self, value):
        self.value = str(value)
    
    def __str__(self):
        return self.value
    
# --- Helper Function for Enum-like Classes ---
def enum_parameter_class(class_name, value_map, default=None):
    """A factory function to create a simple, enum-like class."""
    cls = type(class_name, (), value_map)
    cls.get_name = {v: k for k, v in value_map.items()}.get
    if default is not None:
        cls.default = value_map.get(default)
    return cls


    
# --- Base Instrument Class ---
class KlabInstrument(ABC):
    """The absolute base class for any instrument in klab."""
    def __init__(self, name, address, timeout=5000, **kwargs):
        self.name = name
        self.address = address
        self._visa_instrument = None
        try:
            resource_manager = visa.ResourceManager()
            self._visa_instrument = resource_manager.open_resource(self.address)
            self._visa_instrument.timeout = timeout
            print(f"Successfully connected to {self.name}.")
        except Exception as e:
            print(f"Error connecting to {self.name} at {self.address}: {e}")
            self._visa_instrument = None

    def write(self, cmd: str):
        print(f"  > WRITE: {cmd}")
        if self._visa_instrument is None: return
        self._visa_instrument.write(cmd)

    def ask(self, cmd: str) -> str:
        print(f"  > QUERY: {cmd}")
        if self._visa_instrument is None: return ""
        response = self._visa_instrument.query(cmd)
        print(f"    < RESPONSE: {response.strip()}")
        return response
        
    def close(self):
        if self._visa_instrument:
            self._visa_instrument.close()
    
    def __del__(self):
        self.close()

# --- Dynamic SCPI Command Proxy ---
class SCPICommandProxy:
    """A proxy object to dynamically build and send SCPI commands."""
    def __init__(self, instrument, command_parts=[]):
        self._instrument = instrument
        self._command_parts = command_parts

    def __getattr__(self, name):
        """Appends a new command part when an attribute is accessed."""
        new_parts = self._command_parts + [name.upper()]
        return SCPICommandProxy(self._instrument, new_parts)

    def __getitem__(self, key):
        """Appends an index to the last command part."""
        if not self._command_parts:
            raise ValueError("Cannot use item access on an empty command path.")
        last_part = self._command_parts[-1] + str(key)
        new_parts = self._command_parts[:-1] + [last_part]
        return SCPICommandProxy(self._instrument, new_parts)

    def __call__(self, *args):
        """
        Executes the command when the chain is called as a function.
        - `cmd()`: Getter query -> `CMD?`
        - `cmd(arg)`: Setter -> `CMD arg`
        - `cmd(q, arg)`: Getter query with arguments -> `CMD? arg`
        """
        command_str = ":".join(self._command_parts)
        
        # --- UPDATED LOGIC ---
        if args and args[0] is q:
            # Case 1: Query with arguments. e.g., cmd(q, "param") -> CMD? 'param'
            command_str += "?"
            # Use the rest of the arguments for the query
            query_args = args[1:]
            if query_args:
                formatted_args = []
                for arg in query_args:
                    if isinstance(arg, NoQuote):
                        formatted_args.append(str(arg))
                    elif isinstance(arg, str):
                        formatted_args.append(f"'{arg}'")
                    else:
                        formatted_args.append(str(arg))
                args_str = ",".join(formatted_args)
                command_str += f" {args_str}"
            return self._instrument.ask(command_str)

        elif args:
            # Case 2: Standard setter with arguments. e.g., cmd("param") -> CMD 'param'
            formatted_args = []
            for arg in args:
                if isinstance(arg, NoQuote):
                    formatted_args.append(str(arg))
                elif isinstance(arg, str):
                    formatted_args.append(f"'{arg}'")
                else:
                    formatted_args.append(str(arg))

            args_str = ",".join(formatted_args)
            command_str += f" {args_str}"
            return self._instrument.write(command_str)
        else:
            # Case 3: Standard getter without arguments. e.g., cmd() -> CMD?
            command_str += "?"
            return self._instrument.ask(command_str)


# --- SCPI Instrument Specialization ---
class SCPIInstrument(KlabInstrument):
    """An instrument that uses SCPI and supports dynamic command generation."""
    def __init__(self, name, address, yaml_file=None, **kwargs):
        super().__init__(name, address, **kwargs)
        self.spec = {}
        if yaml_file:
            self._load_spec_from_yaml(yaml_file)

    def _load_spec_from_yaml(self, yaml_file):
        """Loads the instrument specification from a YAML file."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            yaml_path = os.path.join(current_dir, '..', 'tech', yaml_file)
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r') as f:
                    self.spec = yaml.safe_load(f)
                print(f"Loaded specification for '{self.name}' from '{yaml_file}'")
            else:
                raise FileNotFoundError(f"YAML file not found at {yaml_path}")
        except Exception as e:
            print(f"Warning: Could not load YAML spec '{yaml_file}'. Error: {e}")

    def __getattr__(self, name):
        """
        The entry point for all dynamic methods.
        It first checks for a high-level YAML method, then falls back
        to the dynamic SCPI command proxy.
        """
        # Check if the called name is a high-level method defined in the YAML file.
        if 'methods' in self.spec and name in self.spec['methods']:
            # Return a callable function that will execute the YAML sequence.
            def method_caller(**kwargs):
                self._execute_yaml_method(name, **kwargs)
            return method_caller

        # If it's not a YAML method, create the dynamic SCPI command proxy.
        # This is the starting point of the chain.
        return SCPICommandProxy(self, [name.upper()])

    def _execute_yaml_method(self, method_name, **kwargs):
        """Finds and executes a named method from the YAML specification."""
        if 'methods' not in self.spec or method_name not in self.spec['methods']:
            raise AttributeError(f"Method '{method_name}' not found in YAML specification for {self.name}.")
        
        print(f"Executing YAML method: '{method_name}'")
        command_sequence = self.spec['methods'][method_name]
        for command in command_sequence:
            formatted_command = command.format(**kwargs)
            self.write(formatted_command)

    # --- Common SCPI Commands ---
    def get_idn(self) -> dict:
        """Gets the instrument's identification string (*IDN?)."""
        response = self.ask("*IDN?")
        parts = response.strip().split(',')
        return {'vendor': parts[0], 'model': parts[1], 'serial': parts[2], 'firmware': parts[3]}

    def reset(self):
        """Resets the instrument (*RST)."""
        self.write("*RST")
        
    def clear_status(self):
        """Clears the status byte and error queue (*CLS)."""
        self.write("*CLS")

    def wait_for_op_complete(self):
        """Waits for all pending operations to complete (*WAI)."""
        self.write("*WAI")

    def get_status_byte(self) -> int:
        """Gets the status byte of the instrument (STB?)."""
        response = self.ask("*STB?")
        return int(response.strip())

# --- Abstract Classes ---
class SMU(SCPIInstrument):
    """Abstract Base Class for a Source-Measure Unit."""
    @abstractmethod
    def source_voltage(self, voltage: float, current_compliance: float): raise NotImplementedError
    @abstractmethod
    def source_current(self, current: float, voltage_compliance: float): raise NotImplementedError
    @abstractmethod
    def measure_voltage(self, nplc: int) -> float: raise NotImplementedError
    @abstractmethod
    def measure_current(self, nplc: int) -> float: raise NotImplementedError
    @abstractmethod
    def enable_source(self, enable: bool): raise NotImplementedError

class MotorStage(KlabInstrument):
    """Abstract Base Class for a Motorized Stage."""
    @abstractmethod
    def get_position(self, axis: int = 0) -> float: raise NotImplementedError
    @abstractmethod
    def move_to(self, position: float, axis: int = 0): raise NotImplementedError
    @abstractmethod
    def move_by(self, distance: float, axis: int = 0): raise NotImplementedError
    @abstractmethod
    def set_speed(self, speed: float, axis: int = 0): raise NotImplementedError
    @abstractmethod
    def stop(self, axis: int = 0): raise NotImplementedError

if __name__ == "__main__":
    # Example usage of the KlabInstrument and SCPIInstrument classes.
    # This is a driverless example to demonstrate how to use the classes.
    try:
        smu = SCPIInstrument(name="SMU", address="TCPIP::192.168.0.95::INSTR")
        #smu.write(":SOUR:FUNC CURR")
        smu.sour.func(NoQuote('CURR'))  # Set source function to current
        smu.sour.curr(5e-9)
        smu.sour.curr.vlim(0.2)
        smu.sens.func('VOLT')
        smu.sens.volt.nplc(1)
        smu.count(5)
        smu.write(":OUTP ON")
        smu.trac.trig("defbuffer1")
        output = smu.trac.data(q,1,5,"defbuffer1", NoQuote('SOUR'),NoQuote('READ'))  # Fetch data from the trace buffer
        smu.write(":OUTP OFF")
        print(f"Measured voltage: {output} V")
        smu.close()
    except Exception as e:
        print(f"Error occurred: {e}")
        smu.close()
