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
from os import environ

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

        # Check environment variable to control data stream printing
        self._debug_stream = environ.get('KLAB_DEBUG_STREAM', 'False').lower() in ('true', '1', 't')

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
        if self._debug_stream:
            print(f"\t[{self.name}] > WRITE: {command}")
        
        if self._visa_instrument:
            self._visa_instrument.write(command)
        else:
            print(f"Warning: {self.name} is not connected")
        return None
    
    def read(self):
        """Read a response from the instrument."""
        if self._debug_stream:
            print(f"\t[{self.name}] > READ")

        if self._visa_instrument:
            response = self._visa_instrument.read()
            if self._debug_stream:
                # repr() is used to show hidden characters like newlines
                print(f"\t[{self.name}] > RECV : {repr(response)}")
            return response.strip()
        else:
            print(f"Warning: {self.name} is not connected")
            return None
    
    def query(self, command):
        """Send a query and return the response."""
        if self._debug_stream:
            print(f"\t[{self.name}] > QUERY: {command}")

        if self._visa_instrument:
            response =  self._visa_instrument.query(command)
            if self._debug_stream:
                # repr() is used to show hidden characters like newlines
                print(f"\t[{self.name}] > RECV : {repr(response)}")
            return response.strip()
        else:
            print(f"Warning: {self.name} is not connected")
            return None
    
    def close(self):
        """Alias for disconnect to ensure compatibility with other libraries."""
        self.disconnect()

    def wait(self, seconds):
        """Wait for a specified number of seconds."""
        if self._debug_stream:
            print(f"\t[{self.name}] > WAIT: {seconds} seconds")
        
        import time
        time.sleep(seconds)

    def is_connected(self):
        """Check if the instrument is currently connected."""
        return self._visa_instrument is not None and self._visa_instrument.session is not None
        
    def __del__(self):
        """Ensure the instrument is disconnected when the object is deleted."""
        self.disconnect()
        if self._rm:
            self._rm.close()
            self._rm = None

    def __repr__(self):
        """String representation of the instrument."""
        return f"<KlabInstrument name={self.name}, address={self.address}>"    
        
# --- Helper Function for Enum-like Classes ---
def enum_parameter_class(class_name, value_map, default=None):
    """A factory function to create a simple, enum-like class."""
    cls = type(class_name, (), value_map)
    cls.get_name = {v: k for k, v in value_map.items()}.get
    if default is not None:
        cls.default = value_map.get(default)
    return cls