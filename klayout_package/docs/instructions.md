# klab Project Instructions & Developer Guide

## 1. Project Overview

`klab` is a Python package designed to provide a stable and flexible framework for controlling laboratory instruments directly from KLayout. Its primary goal is to simplify instrument communication and automate measurement sequences within the chip design environment.

The core challenge this project overcomes is the difficulty of using standard Python scientific packages (like `qcodes`) inside the specialized, embedded Python environment provided by KLayout, especially on Windows. These environments often lack the necessary compilers and have non-standard library paths, making `pip` installations of complex packages with compiled dependencies unreliable.

To solve this, `klab` adopts a lightweight, self-contained, and hybrid approach to instrument control.

## 2. Core Architecture

The `klab` architecture is designed for robustness and extensibility. It revolves around a few key concepts:

### The `instrument.py` file: The Engine

This is the most important file in the project. It contains the base classes that provide all the core functionality.

* **`KlabInstrument`**: An abstract base class that handles the fundamental VISA connection. All drivers inherit from this.
* **`SCPIInstrument`**: This powerful class inherits from `KlabInstrument` and is the heart of our hybrid driver model. It provides two key features:
    1.  **YAML Method Execution**: It can load a `.yml` file that defines high-level methods as sequences of SCPI commands (e.g., a complete setup sequence for a measurement).
    2.  **Dynamic Command Proxy**: For any method that isn't explicitly defined in the Python driver or the YAML file, this class uses a `SCPICommandProxy` to build and send SCPI commands on-the-fly. This gives users access to the instrument's entire SCPI command set without needing a wrapper for every command.

### The `drivers` Directory: Thin Wrappers

The drivers in the `klab/python/klab/drivers/` directory are designed to be "thin." Their only jobs are:

1.  To inherit from the correct abstract base class (e.g., `SMU` or `VNA`).
2.  To tell the `SCPIInstrument` base class which YAML file to load for its configuration.
3.  To implement any highly complex logic that cannot be easily described in YAML, such as parsing complex binary data blocks from an instrument.

### The `tech` Directory: The "Brains"

The YAML files in the `klab/tech/` directory contain all the instrument-specific knowledge. This is where you define the high-level methods and command sequences. A user or developer can add new functionality to a driver simply by editing its corresponding YAML file, with no Python coding required.

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

Creating a new driver for a SCPI-based instrument is straightforward:

1.  **Create the YAML File**: In the `klab/tech/` directory, create a new file (e.g., `my_new_instrument.yml`). Populate it with the high-level methods you want, defined as sequences of SCPI commands.

2.  **Create the Python Driver File**: In the `klab/python/klab/drivers/` directory, create a new file (e.g., `my_new_instrument.py`).

3.  **Write the "Thin" Driver Code**: In the new Python file, create a class that inherits from the appropriate abstract base class (e.g., `SCPIInstrument`, or a more specific one like `VNA`). The only thing required in the `__init__` method is to call the parent's `__init__` and point it to your new YAML file:
    ```python
    from klab.instrument import SCPIInstrument

    class MyNewInstrument(SCPIInstrument):
        def __init__(self, name, address, **kwargs):
            super().__init__(name, address, yaml_file='my_new_instrument.yml', **kwargs)
            if self._visa_instrument:
                self.initialize() # Assumes 'initialize' is defined in your YAML
    ```

4.  **Update `grain.xml`**: Add your new YAML and Python files to the `<files>` section of the `grain.xml` manifest to ensure they are included in the KLayout package.

By following this pattern, you can rapidly expand `klab` to support a wide range of new instruments while keeping the codebase clean, stable, and easy to maintain.
