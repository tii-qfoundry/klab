"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
# ==================================================================
# This file defines the core architecture for instruments, featuring
# a base class for VISA communication.
# ==================================================================

from os import environ
from .comm import VisaBackend, CommBackend


class KlabInstrument:
    """
    The foundational base class for all klab instruments.

    This class provides the core functionality for instrument communication,
    including connection management, command execution, and a pluggable
    backend system for different communication protocols.

    It is designed to be subclassed by specific instrument drivers, which
    can either use the default `VisaBackend` or provide a custom
    communication backend.

    Attributes:
        name (str): A friendly name for the instrument instance.
        address (str): The connection address for the instrument (e.g., VISA resource string).
        is_connected (bool): True if a connection is currently active.
        communication_backend (CommunicationBackend): The backend used for communication.
    """
    
    def __init__(self, name, address, communication_backend: CommBackend = None, **kwargs):
        """
        Initializes a new instrument instance.

        Args:
            name (str): A friendly name for the instrument (e.g., "Primary SMU").
            address (str): The address required to connect to the instrument.
                         The format depends on the communication backend
                         (e.g., "TCPIP0::192.168.1.100::INSTR" for VISA).
            communication_backend (CommunicationBackend, optional):
                An instance of a communication backend. If None, defaults to
                `VisaBackend`.
            **kwargs: Additional keyword arguments passed to the communication
                      backend's `connect` method.
        """
        self.name = name
        self.address = address
        
        # Use provided backend or default to VISA
        if communication_backend is not None:
            self.communication_backend = communication_backend
        else:
            self.communication_backend = VisaBackend()
        
        # Legacy attributes for backward compatibility
        self._visa_instrument = None
        self._rm = None

        # Check environment variable to control data stream printing
        self._debug_stream = environ.get('KLAB_DEBUG_STREAM', 'False').lower() in ('true', '1', 't')

        # Connect to the instrument if requested
        if kwargs.get('connect', True):
            self.connect(**kwargs)

    def connect(self, **kwargs):
        """
        Establishes a connection to the instrument.

        This method uses the assigned communication backend to open a
        connection. Additional keyword arguments are passed to the
        backend's `connect` method.
        """
        try:
            success = self.communication_backend.connect(self.address, **kwargs)
            self.is_connected = success
            if success:
                print(f"Connected to {self.name} at {self.address}")
                # For backward compatibility with VISA instruments
                if isinstance(self.communication_backend, VisaBackend):
                    self._visa_instrument = self.communication_backend._visa_instrument
                    self._rm = self.communication_backend._rm
            else:
                print(f"Failed to connect to {self.name} at {self.address}")
        except Exception as e:
            print(f"Failed to connect to {self.name} at {self.address}: {e}")
    
    def disconnect(self):
        """
        Closes the connection to the instrument.

        It is crucial to call this method to release instrument resources
        properly.
        """
        try:
            self.communication_backend.disconnect()
            # Clear legacy attributes
            self._visa_instrument = None
            self._rm = None
            self.is_connected = False
            print(f"Disconnected from {self.name}")
        except Exception as e:
            print(f"Error disconnecting from {self.name}: {e}")
    
    def write(self, command: str):
        """
        Sends a command to the instrument.

        Args:
            command (str): The command string to send.
        
        Raises:
            ConnectionError: If the instrument is not connected.
        """
        if self._debug_stream:
            print(f"\t[{self.name}] > WRITE: {command}")
        
        try:
            self.communication_backend.write(command)
        except Exception as e:
            print(f"Warning: Failed to write to {self.name}: {e}")
        return None
    
    def read(self) -> str:
        """
        Reads a response from the instrument.

        Returns:
            str: The response from the instrument.
        
        Raises:
            ConnectionError: If the instrument is not connected.
        """
        if self._debug_stream:
            print(f"\t[{self.name}] > READ")

        try:
            response = self.communication_backend.read()
            if self._debug_stream:
                # repr() is used to show hidden characters like newlines
                print(f"\t[{self.name}] > RECV : {repr(response)}")
            return response
        except Exception as e:
            print(f"Warning: Failed to read from {self.name}: {e}")
            return None
    
    def query(self, command: str) -> str:
        """
        Sends a command and reads the response.

        This is a convenience method combining `write` and `read`.

        Args:
            command (str): The query command to send.

        Returns:
            str: The response from the instrument.
        """
        if self._debug_stream:
            print(f"\t[{self.name}] > QUERY: {command}")

        try:
            response = self.communication_backend.query(command)
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

    def wait(self, seconds: float):
        """
        Pauses execution for a specified duration.

        Args:
            seconds (float): The number of seconds to wait.
        """
        if self._debug_stream:
            print(f"\t[{self.name}] > WAIT: {seconds} seconds")
        
        import time
        time.sleep(seconds)

    def __repr__(self):
        """Provides a developer-friendly representation of the instrument."""
        return f"<KlabInstrument name={self.name}, address={self.address}>"    
        
# --- Helper Function for Enum-like Classes ---
def enum_parameter_class(class_name, value_map, default=None):
    """A factory function to create a simple, enum-like class."""
    cls = type(class_name, (), value_map)
    cls.get_name = {v: k for k, v in value_map.items()}.get
    if default is not None:
        cls.default = value_map.get(default)
    return cls