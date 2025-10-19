# klab Documentation

## 1. Overview

klab is a KLayout package designed to bridge the gap between chip layout and electrical characterization. It provides a stable and flexible framework for controlling laboratory instruments directly from KLayout, streamlining the process of testing and validating integrated circuits.

The core philosophy is to integrate test-rule definitions and instrument control into the design environment, enabling a "measurement-aware" layout workflow while avoiding the complexities of heavyweight scientific packages that are difficult to deploy in KLayout's embedded Python environment.

You need to install at least py_yaml (pakcage python_libraries), pyvisa and packaging, and optionally libximc (for the native controller of Standa Motor Controller distributed as an example). Drivers can be develloped within the klab package, but the project structure allows for them to be part of the technology specification instead, which is better a low weigth base package.

## 2. Core Features

### Flexible Communication Architecture
- **Pluggable Backends**: Support for VISA/SCPI instruments and custom communication protocols
- **Protocol Agnostic**: Easy integration of instruments using TCP/IP, USB, Serial, or specialized protocols like libximc
- **Backward Compatible**: Existing VISA-based instruments work unchanged

### Instrument Control
- **Lightweight Design**: Self-contained framework that avoids complex dependencies
- **Hybrid Driver Model**: Combines Python code with YAML configuration for maximum flexibility
- **Dynamic SCPI Proxy**: Access any SCPI command without writing wrapper code

### PCell-based Instruments
- Instruments are defined as parametric cells (PCells) in your layout
- Instantiating an instrument PCell makes its controls available in the klab measurement interface
- Visual integration between layout and measurement setup

### Technology-Integrated Test Rules
- Define complete measurement procedures in YAML files within your technology
- Standardize test protocols like 'MOSFET Id-Vg sweep' or 'Resistor Linearity Test'
- Include sweep parameters, compliance limits, timing delays, and complete recipes
- Ensure consistency and repeatability across teams and projects

### Organized Abstract Classes
- Clear interfaces for different instrument types (SMU, VNA, MotorStage)
- Each abstract class in its own module for better maintainability
- Easy to extend with new instrument types

### Dynamic UI
- Dedicated "Measurement" tab in KLayout
- Controls dynamically populate based on instrument PCells in your layout
- Real-time instrument status and control

### Extensible Architecture
- Simple process for adding new SCPI instruments (just create a YAML file)
- Custom communication backends for non-SCPI instruments
- Minimal code required for new instrument support

## 3. Installation

klab is distributed as a KLayout Salt package (.kip) [Not yet, for now clone the repo and link to it in the salt folder]

1. **Download**: Get the latest klab-vx.x.x.kip file
2. **Open KLayout**: Launch your KLayout application
3. **Install Package**: 
   - Navigate to Tools > Manage Packages
   - Click "Install New Package" and select the klab-vx.x.x.kip file
4. **Automatic Setup**: KLayout will automatically install the package and check for required Python dependencies (pyvisa, etc.)
5. **Restart**: Restart KLayout to complete the installation
6. **Verify**: A new "Measurement" menu will appear in the main menu bar

## 4. Quick Start

### Basic SMU Usage
```python
from klab.instruments.drivers.keithley_2450 import Keithley2450

# Connect to instrument
smu = Keithley2450(name="My SMU", address="TCPIP0::192.168.1.100::INSTR")

# Use YAML-defined methods
smu.source_voltage(voltage=1.0, current_compliance=0.1)
current = smu.measure_current()

# Use dynamic SCPI commands
smu.system.beeper(500, 1)  # Sends ":SYSTem:BEEPer 500,1"
```

### Motor Stage with Custom Backend
```python
from klab.instruments.drivers.standa_8smc4 import Standa8SMC4

# Uses custom XimcBackend automatically
stage = Standa8SMC4(name="XY Stage", address="virtual_motor_controller_1.bin")
stage.move_to(1000)
position = stage.get_position()
```

## 5. Architecture Benefits

- **Lightweight**: No heavy dependencies that are difficult to install in KLayout
- **Flexible**: Supports any communication protocol through custom backends
- **Maintainable**: Clear separation between instrument logic and communication
- **Extensible**: Easy to add new instruments and protocols
- **Robust**: Proper error handling and resource management
- **Consistent**: Same interface regardless of underlying communication method

## 6. Documentation
