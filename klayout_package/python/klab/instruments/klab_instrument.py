"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
# ==================================================================
# This file defines the core architecture for instruments, featuring
# a base class for VISA communication.
# ==================================================================

import pyvisa

class KlabInstrument:
    """Base class for all klab instruments."""
    
    def __init__(self, name, address, **kwargs):
        """Initialize a new instrument.
        
        Args:
            name: A friendly name for the instrument
            address: VISA address string
            **kwargs: Additional configuration options
        """
        self.name = name
        self.address = address
        self._visa_instrument = None
        self._rm = None
        
        # Connect to the instrument if requested
        if kwargs.get('connect', True):
            self.connect()
    
    def connect(self):
        """Establish a connection to the instrument."""
        try:
            self._rm = pyvisa.ResourceManager()
            self._visa_instrument = self._rm.open_resource(self.address)
            print(f"Connected to {self.name} at {self.address}")
        except Exception as e:
            print(f"Failed to connect to {self.name} at {self.address}: {e}")
            self._visa_instrument = None
    
    def disconnect(self):
        """Close the connection to the instrument."""
        if self._visa_instrument:
            self._visa_instrument.close()
            self._visa_instrument = None
            print(f"Disconnected from {self.name}")
    
    def write(self, command):
        """Send a command to the instrument."""
        if self._visa_instrument:
            self._visa_instrument.write(command)
        else:
            print(f"Warning: {self.name} is not connected")
        return None
    
    def query(self, command):
        """Send a query and return the response."""
        if self._visa_instrument:
            return self._visa_instrument.query(command)
        else:
            print(f"Warning: {self.name} is not connected")
            return None
        
# --- Helper Function for Enum-like Classes ---
def enum_parameter_class(class_name, value_map, default=None):
    """A factory function to create a simple, enum-like class."""
    cls = type(class_name, (), value_map)
    cls.get_name = {v: k for k, v in value_map.items()}.get
    if default is not None:
        cls.default = value_map.get(default)
    return cls