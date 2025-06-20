

from abc import ABC, abstractmethod
from .scpi_instrument import ScpiInstrument
from .klab_instrument import KlabInstrument

class SMU(ScpiInstrument, ABC):
    """Abstract Source-Measure Unit base class."""
    
    @abstractmethod
    def source_voltage(self, voltage: float, current_compliance: float): 
        """Set the SMU to source voltage mode with specified compliance."""
        pass
        
    @abstractmethod
    def source_current(self, current: float, voltage_compliance: float):
        """Set the SMU to source current mode with specified compliance."""
        pass
    
    @abstractmethod
    def measure_voltage(self):
        """Measure voltage from the SMU."""
        pass
        
    @abstractmethod
    def measure_current(self):
        """Measure current from the SMU."""
        pass
        
    @abstractmethod
    def enable_source(self, state: bool):
        """Enable or disable the source output."""
        pass

class VNA(ScpiInstrument, ABC):
    """Abstract Vector Network Analyzer base class."""
    
    @abstractmethod
    def setup_sweep(self, start_freq: float, stop_freq: float, num_points: int):
        """Configure the frequency sweep."""
        pass
    
    @abstractmethod
    def measure_s_parameters(self):
        """Measure S-parameters."""
        pass

# Classes that are not specified using SCPI commands but are still abstract base classes.
# can be defined here as well using the KlabInstrument base class.
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