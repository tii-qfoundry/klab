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

