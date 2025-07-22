"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
from abc import ABC, abstractmethod

class CommBackend(ABC):
    """
    Abstract base class for instrument communication backends.

    This class defines the interface that all communication backends must
    implement. It allows `KlabInstrument` to be protocol-agnostic,
    seamlessly switching between different communication methods like VISA,
    serial, or custom protocols.
    """
    
    @abstractmethod
    def connect(self, address: str, **kwargs) -> bool:
        """
        Establish a connection to the instrument.

        Args:
            address (str): The address of the instrument to connect to.
            **kwargs: Additional backend-specific connection parameters.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """
        Close the connection to the instrument.

        This method should handle all necessary cleanup to release the
        communication resource.
        """
        pass
    
    @abstractmethod
    def write(self, command: str):
        """
        Send a command to the instrument.

        Args:
            command (str): The command string to be sent.
        """
        pass
    
    @abstractmethod
    def read(self) -> str:
        """
        Read a response from the instrument.

        Returns:
            str: The data read from the instrument.
        """
        pass
    
    @abstractmethod
    def query(self, command: str) -> str:
        """
        Send a command and read the response back.

        Args:
            command (str): The query command to send.

        Returns:
            str: The response from the instrument.
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the connection is currently active.

        Returns:
            bool: True if connected, False otherwise.
        """
        pass
