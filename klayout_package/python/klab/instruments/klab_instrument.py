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
from abc import ABC, abstractmethod

class CommunicationBackend(ABC):
    """Abstract base class for instrument communication backends."""
    
    @abstractmethod
    def connect(self, address: str) -> bool:
        """Establish connection to the instrument. Returns True if successful."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the connection to the instrument."""
        pass
    
    @abstractmethod
    def write(self, command: str):
        """Send a command to the instrument."""
        pass
    
    @abstractmethod
    def read(self) -> str:
        """Read a response from the instrument."""
        pass
    
    @abstractmethod
    def query(self, command: str) -> str:
        """Send a query and return the response."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the instrument is currently connected."""
        pass


class VisaBackend(CommunicationBackend):
    """VISA communication backend for SCPI instruments."""
    
    def __init__(self):
        self._visa_instrument = None
        self._rm = None
    
    def connect(self, address: str) -> bool:
        """Establish a VISA connection to the instrument."""
        try:
            self._rm = pyvisa.ResourceManager()
            self._visa_instrument = self._rm.open_resource(address)
            return True
        except Exception as e:
            print(f"VISA connection failed: {e}")
            self._visa_instrument = None
            return False
    
    def disconnect(self):
        """Close the VISA connection."""
        if self._visa_instrument:
            self._visa_instrument.close()
            self._visa_instrument = None
        if self._rm:
            self._rm.close()
            self._rm = None
    
    def write(self, command: str):
        """Send a VISA write command."""
        if self._visa_instrument:
            self._visa_instrument.write(command)
        else:
            raise RuntimeError("VISA instrument not connected")
    
    def read(self) -> str:
        """Read a VISA response."""
        if self._visa_instrument:
            return self._visa_instrument.read().strip()
        else:
            raise RuntimeError("VISA instrument not connected")
    
    def query(self, command: str) -> str:
        """Send a VISA query and return response."""
        if self._visa_instrument:
            return self._visa_instrument.query(command).strip()
        else:
            raise RuntimeError("VISA instrument not connected")
    
    def is_connected(self) -> bool:
        """Check if VISA instrument is connected."""
        return self._visa_instrument is not None and self._visa_instrument.session is not None


class KlabInstrument:
    """Base class for all klab instruments."""
    
    def __init__(self, name, address, communication_backend=None, **kwargs):
        """Initialize a new instrument.
        
        Args:
            name: A friendly name for the instrument
            address: Address string for the instrument
            communication_backend: Custom communication backend instance. 
                                 If None, defaults to VisaBackend for backward compatibility.
            **kwargs: Additional configuration options
        """
        self.name = name
        self.address = address
        
        # Use provided backend or default to VISA
        if communication_backend is not None:
            self._comm_backend = communication_backend
        else:
            self._comm_backend = VisaBackend()
        
        # Legacy attributes for backward compatibility
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
            success = self._comm_backend.connect(self.address)
            if success:
                print(f"Connected to {self.name} at {self.address}")
                # For backward compatibility with VISA instruments
                if isinstance(self._comm_backend, VisaBackend):
                    self._visa_instrument = self._comm_backend._visa_instrument
                    self._rm = self._comm_backend._rm
            else:
                print(f"Failed to connect to {self.name} at {self.address}")
        except Exception as e:
            print(f"Failed to connect to {self.name} at {self.address}: {e}")
    
    def disconnect(self):
        """Close the connection to the instrument."""
        try:
            self._comm_backend.disconnect()
            # Clear legacy attributes
            self._visa_instrument = None
            self._rm = None
            print(f"Disconnected from {self.name}")
        except Exception as e:
            print(f"Error disconnecting from {self.name}: {e}")
    
    def write(self, command):
        """Send a command to the instrument."""
        if self._debug_stream:
            print(f"\t[{self.name}] > WRITE: {command}")
        
        try:
            self._comm_backend.write(command)
        except Exception as e:
            print(f"Warning: Failed to write to {self.name}: {e}")
        return None
    
    def read(self):
        """Read a response from the instrument."""
        if self._debug_stream:
            print(f"\t[{self.name}] > READ")

        try:
            response = self._comm_backend.read()
            if self._debug_stream:
                # repr() is used to show hidden characters like newlines
                print(f"\t[{self.name}] > RECV : {repr(response)}")
            return response
        except Exception as e:
            print(f"Warning: Failed to read from {self.name}: {e}")
            return None
    
    def query(self, command):
        """Send a query and return the response."""
        if self._debug_stream:
            print(f"\t[{self.name}] > QUERY: {command}")

        try:
            response = self._comm_backend.query(command)
            if self._debug_stream:
                # repr() is used to show hidden characters like newlines
                print(f"\t[{self.name}] > RECV : {repr(response)}")
            return response
        except Exception as e:
            print(f"Warning: Failed to query {self.name}: {e}")
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
        try:
            return self._comm_backend.is_connected()
        except Exception:
            return False
        
    def __del__(self):
        """Ensure the instrument is disconnected when the object is deleted."""
        try:
            self.disconnect()
        except Exception:
            pass  # Ignore errors during cleanup

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