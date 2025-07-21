# klab API Reference

## Core Classes

### KlabInstrument

The foundational base class for all klab instruments.

```python
class KlabInstrument:
    def __init__(self, name, address, communication_backend=None, **kwargs):
        """Initialize a new instrument.
        
        Args:
            name: A friendly name for the instrument
            address: Address string for the instrument
            communication_backend: Custom communication backend instance. 
                                 If None, defaults to VisaBackend
            **kwargs: Additional configuration options
        """
```

#### Methods
- `connect()`: Establish connection to the instrument
- `disconnect()`: Close the connection
- `write(command)`: Send a command to the instrument
- `read()`: Read a response from the instrument
- `query(command)`: Send a query and return the response
- `is_connected()`: Check if the instrument is connected
- `wait(seconds)`: Wait for specified time

### CommunicationBackend (Abstract)

Abstract base class for all communication backends.

```python
class CommunicationBackend(ABC):
    @abstractmethod
    def connect(self, address: str) -> bool: pass
    
    @abstractmethod
    def disconnect(self): pass
    
    @abstractmethod
    def write(self, command: str): pass
    
    @abstractmethod
    def read(self) -> str: pass
    
    @abstractmethod
    def query(self, command: str) -> str: pass
    
    @abstractmethod
    def is_connected(self) -> bool: pass
```

### VisaBackend

Default VISA communication backend for SCPI instruments.

```python
class VisaBackend(CommunicationBackend):
    def __init__(self):
        """Initialize VISA backend."""
```

## Abstract Instrument Classes

### SMU (Source-Measure Unit)

```python
from klab.instruments.abstract_classes import SMU

class SMU(ScpiInstrument, ABC):
    @abstractmethod
    def source_voltage(self, voltage: float, current_compliance: float):
        """Set voltage source mode with current compliance."""
    
    @abstractmethod
    def source_current(self, current: float, voltage_compliance: float):
        """Set current source mode with voltage compliance."""
    
    @abstractmethod
    def measure_voltage(self):
        """Measure voltage."""
    
    @abstractmethod
    def measure_current(self):
        """Measure current."""
    
    @abstractmethod
    def enable_source(self, state: bool):
        """Enable or disable the source output."""
```

### VNA (Vector Network Analyzer)

```python
from klab.instruments.abstract_classes import VNA

class VNA(ScpiInstrument, ABC):
    @abstractmethod
    def setup_sweep(self, start_freq: float, stop_freq: float, num_points: int):
        """Configure frequency sweep parameters."""
    
    @abstractmethod
    def measure_s_parameters(self):
        """Measure S-parameters."""
```

### MotorStage

```python
from klab.instruments.abstract_classes import MotorStage

class MotorStage(KlabInstrument, ABC):
    @abstractmethod
    def get_position(self, axis: int = 0) -> float:
        """Get current position."""
    
    @abstractmethod
    def move_to(self, position: float, axis: int = 0):
        """Move to absolute position."""
    
    @abstractmethod
    def move_by(self, distance: float, axis: int = 0):
        """Move by relative distance."""
    
    @abstractmethod
    def set_speed(self, speed: float, axis: int = 0):
        """Set movement speed."""
    
    @abstractmethod
    def stop(self, axis: int = 0):
        """Stop movement."""
    
    @abstractmethod
    def home(self, axis: int = 0):
        """Home the axis."""
```

## Concrete Driver Classes

### Keithley2450

SMU driver for Keithley 2450 instrument.

```python
from klab.instruments.drivers.keithley_2450 import Keithley2450

smu = Keithley2450(name="My SMU", address="TCPIP0::192.168.1.100::INSTR")

# YAML-defined methods
smu.source_voltage(voltage=1.0, current_compliance=0.1)
smu.source_current(current=1e-3, voltage_compliance=10.0)

# Measurement methods
voltage = smu.measure_voltage(current=1e-3)
current = smu.measure_current(voltage=1.0)

# Control methods
smu.enable_source(True)
smu.reset()
```

### Standa8SMC4

Motor stage driver for Standa 8SMC4 controllers using libximc.

```python
from klab.instruments.drivers.standa_8smc4 import Standa8SMC4

stage = Standa8SMC4(name="XY Stage", address="virtual_motor_controller_1.bin")

# Position control
position = stage.get_position()
stage.move_to(1000)
stage.move_by(500)

# Motion control
stage.set_speed(1000)
stage.stop()
stage.home()

# Status
is_moving = stage.is_moving()
status = stage.get_status()
```

## YAML Configuration

For SCPI instruments, you can define high-level methods in YAML files:

```yaml
# Example: keithley_2450.yml
methods:
  initialize:
    description: "Initialize the instrument"
    commands:
      - "*RST"
      - "*CLS"
      - ":SYST:PRES"
  
  source_voltage:
    description: "Configure voltage source mode"
    parameters:
      - name: voltage
        type: float
        description: "Voltage level in volts"
      - name: current_compliance  
        type: float
        description: "Current compliance in amperes"
    commands:
      - ":SOUR:FUNC VOLT"
      - ":SOUR:VOLT {voltage}"
      - ":SENS:CURR:PROT {current_compliance}"
      - ":OUTP ON"
```

## Environment Variables

- `KLAB_DEBUG_STREAM`: Set to 'true' to enable communication debugging
  ```bash
  export KLAB_DEBUG_STREAM=true
  ```

## Error Handling

All klab classes implement robust error handling:

```python
try:
    smu = Keithley2450(name="SMU", address="TCPIP0::192.168.1.100::INSTR")
    if smu.is_connected():
        smu.source_voltage(1.0, 0.1)
    else:
        print("Failed to connect")
except Exception as e:
    print(f"Error: {e}")
finally:
    smu.disconnect()
```

## Best Practices

### Resource Management
```python
# Always disconnect when done
try:
    smu = Keithley2450(name="SMU", address="...")
    # Use instrument...
finally:
    smu.disconnect()

# Or use context managers (if implemented)
with Keithley2450(name="SMU", address="...") as smu:
    # Use instrument...
    pass  # Automatic cleanup
```

### Custom Backend Example
```python
class SerialBackend(CommunicationBackend):
    def __init__(self, baudrate=9600):
        self.baudrate = baudrate
        self.serial_port = None
    
    def connect(self, address: str) -> bool:
        try:
            import serial
            self.serial_port = serial.Serial(address, self.baudrate)
            return True
        except Exception:
            return False
    
    def disconnect(self):
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
    
    # Implement other methods...

# Usage
backend = SerialBackend(baudrate=115200)
instrument = KlabInstrument("Custom", "COM3", communication_backend=backend)
```

## Troubleshooting

### Connection Issues
- Verify instrument address format
- Check network connectivity for TCP/IP instruments
- Ensure VISA runtime is installed
- Enable debug mode: `export KLAB_DEBUG_STREAM=true`

### Import Errors
- Verify klab is properly installed in KLayout
- Check Python path configuration
- Ensure all dependencies are available

### Performance Issues
- Use appropriate timeouts for slow instruments
- Implement connection pooling for multiple instruments
- Consider async operations for long measurements
