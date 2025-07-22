# klab Project Instructions & Developer Guide

## 1. Project Overview

`klab` is a Python package designed to provide a stable and flexible framework for controlling laboratory instruments directly from KLayout. Its primary goal is to simplify instrument communication and automate measurement sequences within the chip design environment.

The core challenge this project overcomes is the difficulty of using standard Python scientific packages (like `qcodes`) inside the specialized, embedded Python environment provided by KLayout, especially on Windows. These environments often lack the necessary compilers and have non-standard library paths, making `pip` installations of complex packages with compiled dependencies unreliable.

To solve this, `klab` adopts a lightweight, self-contained, and hybrid approach to instrument control.

The klab package includes abstract base classes for various instruments, such as Source-Measure Units (SMU), Vector Network Analyzers (VNA), and Motor Stages, allowing for a consistent interface across different instrument drivers. klab is designed to facilitate the development of instrument drivers and to provide a framework for integrating lab instrumentation with KLayout workflows. It supports a low weigth and flexible SCPI (Standard Commands for Programmable Instruments) interface, ensuring compatibility with a wide 
range of test and measurement devices.

## 2. Core Architecture

The `klab` architecture is designed for robustness and extensibility. It revolves around a few key concepts:

### Communication Backend System

The foundation of klab's flexibility lies in its pluggable communication backend system:

* **`CommunicationBackend`**: An abstract base class that defines the interface for all communication protocols. This allows klab to support different communication methods beyond just VISA.
* **`VisaBackend`**: The default implementation that handles traditional VISA/SCPI communication for most test instruments.
* **Custom Backends**: You can create specialized backends for protocols like libximc (for motor controllers), serial communication, or any other protocol your instruments require.

### The Core Instrument Classes

* **`KlabInstrument`**: The foundational base class that provides communication functionality through pluggable backends. It handles connection management, debugging, and provides a consistent interface regardless of the underlying communication protocol.
* **`ScpiInstrument`**: This powerful class inherits from `KlabInstrument` and is the heart of our hybrid driver model for SCPI-based instruments. It provides two key features:
    1.  **YAML Method Execution**: It can load a `.yml` file that defines high-level methods as sequences of SCPI commands (e.g., a complete setup sequence for a measurement).
    2.  **Dynamic Command Proxy**: For any method that isn't explicitly defined in the Python driver or the YAML file, this class uses a `SCPICommandProxy` to build and send SCPI commands on-the-fly. This gives users access to the instrument's entire SCPI command set without needing a wrapper for every command.

### Abstract Classes Organization

The abstract classes are now organized in dedicated modules for better maintainability:

```
klab/instruments/abstract_classes/
├── __init__.py           # Package exports
├── smu.py               # Source-Measure Unit interface
├── vna.py               # Vector Network Analyzer interface
└── motor_stage.py       # Motorized Stage interface
```

Each abstract class defines the standard interface for its instrument type, ensuring consistency across different manufacturers and models.

### The `drivers` Directory: Thin Wrappers

The drivers in the `klab/instruments/drivers/` directory are designed to be "thin." Their primary responsibilities are:

1.  To inherit from the correct abstract base class (e.g., `SMU`, `VNA`, or `MotorStage`).
2.  To configure the appropriate communication backend (VISA by default, or custom backends for special protocols).
3.  To tell the `ScpiInstrument` base class which YAML file to load for its configuration (for SCPI instruments).
4.  To implement any highly complex logic that cannot be easily described in YAML, such as parsing complex binary data blocks from an instrument.

### The `tech` Directory: The "Brains"

The YAML files in the `klab/tech/` directory contain all the instrument-specific knowledge for SCPI instruments. This is where you define the high-level methods and command sequences. A user or developer can add new functionality to a driver simply by editing its corresponding YAML file, with no Python coding required.

## 3. How to Use a Driver

The hybrid design provides three flexible ways to interact with an instrument instance (e.g., `smu`):

1.  **Call an Explicit Python Method**: If a method is defined in the Python driver file (like `set_average_count` in the Keithley driver), you can call it directly. This is best for complex functions.
    ```python
    smu.set_average_count('VOLT', 10)
    ```

2.  **Call a YAML-defined Method**: If a method is defined in the instrument's YAML file (like `enable_source`), the base class makes it available to be called as if it were a normal Python method.
    ```python
    smu.enable_source(state='ON')
    ```

3.  **Use the Dynamic SCPI Proxy**: For any other SCPI command, you can build it on the fly. The proxy automatically handles formatting and sending the command.
    ```python
    # Sends the command: :SYSTem:BEEPer 500,1
    smu.system.beeper(500, 1)

    # For queries, call the method without arguments.
    # Sends the command: :SYSTem:ERRor?
    error = smu.system.error()
    ```

## 4. How to Create a New Driver

The process for creating a new driver depends on whether your instrument uses SCPI commands or a custom protocol:

### For SCPI-Based Instruments

Creating a new driver for a SCPI-based instrument is straightforward:

1.  **Create the YAML File**: In the `klab/tech/` directory, create a new file (e.g., `my_new_instrument.yml`). Populate it with the high-level methods you want, defined as sequences of SCPI commands.

2.  **Create the Python Driver File**: In the `klab/instruments/drivers/` directory, create a new file (e.g., `my_new_instrument.py`).

3.  **Write the "Thin" Driver Code**: In the new Python file, create a class that inherits from the appropriate abstract base class (e.g., `ScpiInstrument`, or a more specific one like `SMU` or `VNA`). The only thing required in the `__init__` method is to call the parent's `__init__` and point it to your new YAML file:
    ```python
    from klab.instruments.abstract_classes import SMU
    from klab.instruments.yaml_utils import yaml_method

    class MyNewSMU(SMU):
        def __init__(self, name, address, **kwargs):
            super().__init__(name, address, yaml_file='my_new_instrument.yml', **kwargs)
            if self._visa_instrument:
                self.initialize() # Assumes 'initialize' is defined in your YAML
    ```

4.  **Update `grain.xml`**: Add your new YAML and Python files to the `<files>` section of the `grain.xml` manifest to ensure they are included in the KLayout package.

### For Non-SCPI Instruments (Custom Communication)

For instruments that don't use SCPI (like motor controllers, custom hardware, etc.):

1.  **Create a Custom Communication Backend**: Implement the `CommunicationBackend` interface for your specific protocol:
    ```python
    from klab.instruments.klab_instrument import CommunicationBackend
    
    class MyCustomBackend(CommunicationBackend):
        def connect(self, address: str) -> bool:
            # Implement your connection logic
            pass
        
        def disconnect(self):
            # Implement disconnection logic
            pass
        
        # Implement other required methods...
    ```

2.  **Create the Instrument Driver**: Inherit from the appropriate abstract class and use your custom backend:
    ```python
    from klab.instruments.abstract_classes import MotorStage
    
    class MyCustomMotor(MotorStage):
        def __init__(self, name, address, **kwargs):
            # Create your custom backend
            custom_backend = MyCustomBackend()
            
            # Initialize with the custom backend
            super().__init__(name, address, communication_backend=custom_backend, **kwargs)
        
        # Implement the abstract methods required by MotorStage
        def get_position(self, axis: int = 0) -> float:
            # Your implementation here
            pass
    ```

By following this pattern, you can rapidly expand `klab` to support a wide range of new instruments while keeping the codebase clean, stable, and easy to maintain.

## 5. Communication Backends: Beyond VISA

One of klab's key innovations is its pluggable communication backend system, which allows you to support instruments that don't use traditional VISA/SCPI communication.

### Available Backends

#### VisaBackend (Default)
- **Purpose**: Handles traditional VISA communication for SCPI instruments
- **Usage**: Automatically used by default for all instruments
- **Supports**: TCP/IP, USB, Serial, Ethernet SCPI instruments

#### Custom Backends
You can create custom backends for any communication protocol by implementing the `CommunicationBackend` interface:

```python
from klab.instruments.klab_instrument import CommunicationBackend

class XimcBackend(CommunicationBackend):
    """Example: Backend for libximc motor controllers"""
    
    def connect(self, address: str) -> bool:
        # Custom connection logic for your protocol
        return True
    
    def disconnect(self):
        # Custom disconnection logic
        pass
    
    def write(self, command: str):
        # For non-text protocols, this might be a no-op
        pass
    
    def read(self) -> str:
        # Return appropriate response or empty string
        return ""
    
    def query(self, command: str) -> str:
        # Combined write/read operation
        return ""
    
    def is_connected(self) -> bool:
        # Check connection status
        return True
```

### Using Custom Backends

When creating an instrument that needs a custom backend:

```python
# Create your custom backend
custom_backend = XimcBackend()

# Pass it to the instrument constructor
motor = MyMotorStage(
    name="Custom Motor", 
    address="192.168.1.100:1820",
    communication_backend=custom_backend
)
```

### Benefits of the Backend System

1. **Protocol Flexibility**: Support any communication protocol, not just VISA
2. **Consistent Interface**: Same `write()`, `read()`, `query()` methods regardless of backend
3. **Backward Compatibility**: Existing VISA instruments work unchanged
4. **Easy Testing**: Mock backends for unit testing
5. **Future-Proof**: Easy to add support for new protocols

## 6. Working with Abstract Classes

klab provides abstract base classes that define standard interfaces for different instrument types:

### Available Abstract Classes

#### SMU (Source-Measure Unit)
```python
from klab.instruments.abstract_classes import SMU

class MyKeithley(SMU):
    # Must implement: source_voltage, source_current, 
    # measure_voltage, measure_current, enable_source
    pass
```

#### VNA (Vector Network Analyzer)
```python
from klab.instruments.abstract_classes import VNA

class MyVNA(VNA):
    # Must implement: setup_sweep, measure_s_parameters
    pass
```

#### MotorStage
```python
from klab.instruments.abstract_classes import MotorStage

class MyStage(MotorStage):
    # Must implement: get_position, move_to, move_by, 
    # set_speed, stop, home
    pass
```

### Creating New Abstract Classes

To add a new instrument type:

1. Create a new file in `klab/instruments/abstract_classes/`
2. Define your abstract class with required methods
3. Add the import to `__init__.py`

## 7. Best Practices

### Error Handling
- Always implement proper connection validation
- Use try-catch blocks for communication operations
- Provide meaningful error messages

### Resource Management
- Ensure instruments are properly disconnected
- Use context managers when appropriate
- Clean up resources in `__del__` methods

### Documentation
- Document all abstract methods with clear parameter descriptions
- Provide usage examples in docstrings
- Maintain YAML file documentation for SCPI methods

### Testing
- Create mock backends for unit testing
- Test with virtual devices before real hardware
- Validate connection health regularly

## 8. Examples

### Basic SCPI Instrument
```python
from klab.instruments.abstract_classes import SMU

# Using default VISA backend
smu = Keithley2450(name="My SMU", address="TCPIP0::192.168.1.100::INSTR")
smu.source_voltage(1.0, 0.1)  # 1V with 0.1A compliance
current = smu.measure_current()
```

### Motor Stage with Custom Backend
```python
from klab.instruments.drivers.standa_8smc4 import Standa8SMC4

# Uses custom XimcBackend automatically
stage = Standa8SMC4(name="XY Stage", address="virtual_motor_controller_1.bin")
stage.move_to(1000)  # Move to position 1000
position = stage.get_position()
```

### Dynamic SCPI Commands
```python
# For any SCPI command not explicitly defined
smu.system.beeper(500, 1)  # Sends ":SYSTem:BEEPer 500,1"
error = smu.system.error()  # Sends ":SYSTem:ERRor?" and returns response
```

This architecture provides maximum flexibility while maintaining simplicity and consistency across all instrument types.