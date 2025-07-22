"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
import pyvisa
from .comm_backend import CommBackend

class VisaBackend(CommBackend):
    """
    A communication backend for VISA-compliant instruments.

    This is the default backend used by `KlabInstrument`. It uses the
    `pyvisa` library to communicate with instruments over TCP/IP, USB,
    or other VISA-supported interfaces.

    Attributes:
        _visa_instrument: The `pyvisa` resource instance.
        _rm: The `pyvisa` ResourceManager.
    """
    
    def __init__(self):
        self._visa_instrument = None
        self._rm = None
    
    def connect(self, address: str, **kwargs) -> bool:
        """
        Establish a VISA connection to the instrument.

        Args:
            address (str): The VISA resource string (e.g., "TCPIP0::...").
            **kwargs: Additional arguments for `pyvisa.ResourceManager.open_resource`.

        Returns:
            bool: True if connection succeeds, False otherwise.
        """
        try:
            self._rm = pyvisa.ResourceManager()
            self._visa_instrument = self._rm.open_resource(address, **kwargs)
            return True
        except Exception as e:
            print(f"VISA connection failed: {e}")
            self._visa_instrument = None
            return False
    
    def disconnect(self):
        """Closes the VISA connection."""
        if self._visa_instrument:
            self._visa_instrument.close()
            self._visa_instrument = None
        if self._rm:
            self._rm.close()
            self._rm = None
    
    def write(self, command: str):
        """
        Writes a command to the VISA instrument.

        Args:
            command (str): The command to send.
        """
        if self._visa_instrument:
            self._visa_instrument.write(command)
        else:
            raise RuntimeError("VISA instrument not connected")

    def read(self) -> str:
        """
        Reads data from the VISA instrument.

        Returns:
            str: The response from the instrument.
        """
        if self._visa_instrument:
            return self._visa_instrument.read()
        else:
            raise RuntimeError("VISA instrument not connected")

    def query(self, command: str) -> str:
        """
        Sends a query to the VISA instrument and returns the response.

        Args:
            command (str): The query to send.

        Returns:
            str: The instrument's response.
        """
        if self._visa_instrument:
            return self._visa_instrument.query(command)
        else:
            raise RuntimeError("VISA instrument not connected")

    def is_connected(self) -> bool:
        """
        Checks if the VISA instrument is connected.

        Returns:
            bool: True if the instrument session is active, False otherwise.
        """
        return self._visa_instrument is not None
