"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""

# ==================================================================
# This file defines the core architecture for SCPI Instruments. 
# It extends the base KlabInstrument class to support SCPI commands
# and provides a dynamic proxy mechanism for command generation, and
# YAML-based method definitions.
# ==================================================================

from pyvisa import VisaIOError
from .klab_instrument import KlabInstrument
from .yaml_utils import load_yaml_spec
import re
import time


class _QueryMarker: pass
q = _QueryMarker()


class NoQuote:
    """
    A wrapper to prevent strings from being quoted in SCPI commands.

    SCPI commands sometimes require arguments that are not strings, but look
    like them (e.g., `VOLT` in `:SOUR:FUNC VOLT`). This wrapper ensures that
    such arguments are sent without surrounding quotes.

    Example:
        >>> smu.source.function(NoQuote('VOLT'))
        # Sends the command: :SOUR:FUNC VOLT
    """
    def __init__(self, value):
        self.value = str(value)
    
    def __str__(self):
        return self.value

class SCPICommandProxy:
    """
    A dynamic proxy for building and executing SCPI commands fluently.

    This class enables a more intuitive, attribute-based syntax for constructing
    SCPI commands. Instead of manually writing command strings like
    `instrument.write(":SOUR:VOLT 1.0")`, you can use a chain of attributes:
    `instrument.source.voltage(1.0)`.

    The proxy automatically handles command termination:
    - If called with arguments, it constructs a 'set' command.
    - If called without arguments, it appends a '?' to form a 'query' command.
    """
    
    def __init__(self, instrument, prefix=""):
        self._instrument = instrument
        self._prefix = prefix
    
    def __getattr__(self, name):
        """Chains attributes to build the SCPI command string."""
        new_prefix = f"{self._prefix}:{name}" if self._prefix else name
        return SCPICommandProxy(self._instrument, new_prefix)
    
    def __call__(self, *args):
        """Executes the command as a write or query."""
        command = self._prefix
    
        if args:
            # Format args and append to command
            params = ", ".join(str(arg) for arg in args)
            command = f"{command} {params}"
        
        # If no args, assume it's a query
        if not args:
            command = f"{command}?"
            return self._instrument.query(command)
        else:
            self._instrument.write(command)
            return None

class ScpiInstrument(KlabInstrument):
    """
    A base class for SCPI-based instruments with dynamic and YAML-driven methods.

    This class extends `KlabInstrument` to provide powerful features for
    interacting with instruments that follow the SCPI standard.

    Features:
        - **Dynamic Command Proxy**: Access any SCPI command via chained
          attribute calls (e.g., `instr.system.beeper()`).
        - **YAML-defined Methods**: Define complex, high-level methods in external
          YAML files for clean separation of logic and code.
        - **Standard SCPI Commands**: Pre-implemented common commands like
          `get_idn()`, `reset()`, and `clear_status()`.

    Args:
        name (str): A friendly name for the instrument.
        address (str): The VISA resource string for the instrument.
        yaml_file (str, optional): The path to a YAML file defining custom methods.
        **kwargs: Additional arguments passed to the `KlabInstrument` constructor.
    """
    
    def __init__(self, name, address, yaml_file=None, **kwargs):
        super().__init__(name, address, **kwargs)
        self.spec = {}
        self.yaml_methods = []
        self._yaml_file = yaml_file
        
        if yaml_file:
            self._load_spec_from_yaml(yaml_file)
            self._discover_yaml_methods()
            self._validate_yaml_methods()
    
    def _load_spec_from_yaml(self, yaml_file):
        """Loads the instrument specification from a YAML file."""
        self.spec = load_yaml_spec(yaml_file)
    
    def _discover_yaml_methods(self):
        """Discovers and lists methods defined in the associated YAML file."""
        if 'methods' in self.spec:
            self.yaml_methods = list(self.spec['methods'].keys())
            print(f"\nAvailable YAML-defined methods for {self.name}:")
            for method in self.yaml_methods:
                print(f"  - {method}")
    
    def _validate_yaml_methods(self):
        """Ensures that methods decorated with @yaml_method have a YAML implementation."""
        yaml_required_methods = []
        
        # Find all methods marked with @yaml_method
        for attr_name in dir(self.__class__):
            if attr_name.startswith('__'):
                continue
                
            attr = getattr(self.__class__, attr_name)
            if callable(attr) and hasattr(attr, '_is_yaml_method'):
                yaml_required_methods.append(attr_name)
        
        # Check that they have corresponding YAML implementations
        missing_methods = []
        for method_name in yaml_required_methods:
            if 'methods' not in self.spec or method_name not in self.spec['methods']:
                missing_methods.append(method_name)
        
        if missing_methods:
            raise NotImplementedError(
                f"The following methods are marked as @yaml_method but have no "
                f"implementation in the YAML file '{self._yaml_file}': {missing_methods}"
            )
    
    def _execute_yaml_method(self, method_name, **kwargs):
        """
        Executes a command sequence defined in the instrument's YAML file.

        Args:
            method_name (str): The name of the method to execute.
            **kwargs: Arguments to be formatted into the command strings.

        Returns:
            list or None: A list of results from any query commands, or a single
                          value if only one query was made. Returns None if all
                          commands were write operations.
        """
        if 'methods' not in self.spec or method_name not in self.spec['methods']:
            raise AttributeError(f"Method '{method_name}' not defined in YAML spec")
        
        method_spec = self.spec['methods'][method_name]
        
        # Execute each command in the method
        result = None
        # Handle different YAML structure formats
        if isinstance(method_spec, list):
            # If method_spec is directly a list of command specs
            command_sequence = method_spec
        elif isinstance(method_spec, dict) and 'commands' in method_spec:
            # If method_spec is a dict with a 'commands' key
            command_sequence = method_spec['commands']
        else:
            raise ValueError(f"Invalid YAML structure for method '{method_name}'")
        
        results = []
        for cmd_item in command_sequence:
        # Handle different command specification formats

            if isinstance(cmd_item, str):
                cmd_template: str = cmd_item  # Short notation - just the command string

                # Determine if the command is a query or write command
                if cmd_template.strip().endswith('?') or cmd_template.split(' ')[0].endswith('?'):
                    cmd_type = 'query'
                else:
                    cmd_type = 'write'
                          
            elif isinstance(cmd_item, dict):
                cmd_type = cmd_item.get('type', 'write')
                cmd_template = cmd_item.get('cmd', '')
            else:
                raise ValueError(f"Invalid command specification: {cmd_item}")
            formatted_command = cmd_template.format(**kwargs)

            if '(' in formatted_command and ')' in formatted_command:
                last_response = self._safe_nested_call(formatted_command)
            else:
                last_response = self.write(formatted_command) if cmd_type == 'write' else self.query(formatted_command)
            
            if last_response is not None and (not isinstance(last_response, list) or last_response):
                results.append(last_response) 
        return results
    
    def _safe_nested_call(self, call_string: str):
        """
        Safely parses and calls a nested method string from YAML without using eval().
        
        This allows YAML methods to call other Python or YAML methods on the same
        instrument instance, enabling command reuse and more complex sequences.

        Example:
            `"set_current(current=1e-6, vlim=0.1)"` in YAML will call
            `self.set_current(current=1e-6, vlim=0.1)`.
        """
        match = re.match(r"^\s*([\w\.]+)\((.*)\)\s*$", call_string)
        if not match:
            raise ValueError(f"Invalid nested method format in YAML: '{call_string}'")

        method_name, args_str = match.groups()
        method_to_call = getattr(self, method_name)
        
        # Parse keyword arguments
        kwargs_to_pass = {}
        if args_str.strip():
            # This parser is simple and assumes no commas within argument values
            arg_pairs = [p.strip() for p in args_str.split(',')]
            for pair in arg_pairs:
                key, value_str = [p.strip() for p in pair.split('=', 1)]
                # Try to convert value to a number, otherwise treat as a string
                try:
                    value = float(value_str)
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    value = value_str.strip("'\"") # Strip quotes
                kwargs_to_pass[key] = value

        return method_to_call(**kwargs_to_pass)

    def get_available_methods(self):
        """
        Returns a dictionary detailing the available methods for the instrument.

        This includes methods defined in Python, methods defined in the YAML
        file, and a combined list of all available methods.

        Returns:
            dict: A dictionary with keys 'yaml_methods', 'python_methods',
                  and 'all_methods'.
        """
        python_methods = [
            method for method in dir(self) 
            if callable(getattr(self, method)) 
            and not method.startswith('_')
            and method not in dir(KlabInstrument)
        ]
        
        return {
            'yaml_methods': self.yaml_methods,
            'python_methods': python_methods,
            'all_methods': list(set(self.yaml_methods + python_methods))
        }
    
    def __getattr__(self, name):
        """
        Overrides attribute access to prioritize YAML methods over the SCPI proxy.

        If a method name exists in the loaded YAML specification, it returns a
        callable that executes the YAML method. Otherwise, it falls back to
        the `SCPICommandProxy` to handle dynamic command generation.
        """
        # First check if the attribute exists in the YAML methods
        if 'methods' in self.spec and name in self.spec['methods']:
            def method_caller(**kwargs):
                return self._execute_yaml_method(name, **kwargs)
            return method_caller
        
        # Otherwise, return a command proxy
        return SCPICommandProxy(self, name)
    
    # --- Common SCPI Commands ---
    def get_idn(self) -> dict:
        """
        Queries the instrument's identification string (*IDN?).

        Returns:
            dict: A dictionary containing the 'vendor', 'model', 'serial',
                  and 'firmware' information.
        """
        response = self.ask("*IDN?")
        parts = response.strip().split(',')
        return {'vendor': parts[0], 'model': parts[1], 'serial': parts[2], 'firmware': parts[3]}

    def reset(self):
        """Sends a reset command (*RST) to the instrument."""
        self.write("*RST")
        
    def clear_status(self):
        """Clears the status byte and error queue (*CLS)."""
        self.write("*CLS")

    def wait_for_op_complete(self):
        """Blocks until all pending operations are complete (*WAI)."""
        self.write("*WAI")

    def get_status_byte(self) -> int:
        """
        Queries the instrument's status byte (*STB?).

        Returns:
            int: The integer value of the status byte.
        """
        response = self.ask("*STB?")
        return int(response.strip())
    
    def query(self, command, retries=5, delay=0.5):
        """
        Sends a query and returns the response, with added robustness.

        This method overrides the base query to provide retry logic for
        `VisaIOError`, which can occur during long measurements. It also
        clears the VISA buffer on error to prevent reading stale data.

        Args:
            command (str): The SCPI query command to send.
            retries (int): The number of times to retry on a `VisaIOError`.
            delay (float): The delay in seconds between retries.

        Returns:
            str: The instrument's response, stripped of whitespace.
        
        Raises:
            ConnectionError: If the query fails after all retries.
        """
        if not self._visa_instrument:
            print(f"Warning: {self.name} is not connected")
            return None
        
        # super().write(command)
        attempt = 0
        while attempt < retries:
            try:
                result = self._visa_instrument.query(command)
                return result.strip()
            except VisaIOError as e:
                print(f"VISA IO Error during query: {e} (attempt {attempt+1}/{retries})")
                # Before retrying, clear the instrument buffer to avoid reading stale data.
                try:
                    self._visa_instrument.clear()
                except Exception as clear_e:
                    print(f"Could not clear VISA buffer: {clear_e}")
                
                time.sleep(delay)
                attempt += 1
        
        raise ConnectionError(f"Failed to query '{command}' after {retries} attempts due to repeated VISA IO Errors.")