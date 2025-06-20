
# ==================================================================
# This file defines the core architecture for SCPI Instruments. 
# It extends the base KlabInstrument class to support SCPI commands
# and provides a dynamic proxy mechanism for command generation, and
# YAML-based method definitions.
# ==================================================================

from .klab_instrument import KlabInstrument
from .yaml_utils import load_yaml_spec
import re
import time

from pyvisa import VisaIOError

class _QueryMarker: pass
q = _QueryMarker()


class NoQuote:
    """
    A wrapper class to indicate that a string argument should not be
    enclosed in quotation marks when sent in a SCPI command.
    
    Example:
        smu.source.function(NoQuote('VOLT')) # Sends: :SOUR:FUNC VOLT
    """
    def __init__(self, value):
        self.value = str(value)
    
    def __str__(self):
        return self.value

class SCPICommandProxy:
    """Dynamic proxy for SCPI commands."""
    
    def __init__(self, instrument, prefix=""):
        self._instrument = instrument
        self._prefix = prefix
    
    def __getattr__(self, name):
        new_prefix = f"{self._prefix}:{name}" if self._prefix else name
        return SCPICommandProxy(self._instrument, new_prefix)
    
    def __call__(self, *args):
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
    """An instrument that uses SCPI and supports dynamic command generation."""
    
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
        """Load instrument specification from a YAML file."""
        self.spec = load_yaml_spec(yaml_file)
    
    def _discover_yaml_methods(self):
        """Discover and list methods defined in the YAML spec file."""
        if 'methods' in self.spec:
            self.yaml_methods = list(self.spec['methods'].keys())
            print(f"\nAvailable YAML-defined methods for {self.name}:")
            for method in self.yaml_methods:
                print(f"  - {method}")
    
    def _validate_yaml_methods(self):
        """Validate that all methods marked as YAML methods have YAML implementations."""
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
        """Execute a method defined in the YAML spec."""
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
                print(f"  > Executing nested method: {formatted_command}")
                last_response = self._safe_nested_call(formatted_command)
            else:
                print(f"  > Executing command: {formatted_command}")
                last_response = self.write(formatted_command) if cmd_type == 'write' else self.query(formatted_command)
            
            if last_response is not None and (not isinstance(last_response, list) or last_response):
                results.append(last_response) 
        return results
    
    def _safe_nested_call(self, call_string: str):
        """
        Safely parses and calls a nested method string from YAML without using eval().
        Example: "set_current(current=1e-6, vlim=0.1)"
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
        """Returns a dictionary with information about available methods."""
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
        """Dynamically generate SCPI commands."""
        # First check if the attribute exists in the YAML methods
        if 'methods' in self.spec and name in self.spec['methods']:
            def method_caller(**kwargs):
                return self._execute_yaml_method(name, **kwargs)
            return method_caller
        
        # Otherwise, return a command proxy
        return SCPICommandProxy(self, name)
    
    # --- Common SCPI Commands ---
    def get_idn(self) -> dict:
        """Gets the instrument's identification string (*IDN?)."""
        response = self.ask("*IDN?")
        parts = response.strip().split(',')
        return {'vendor': parts[0], 'model': parts[1], 'serial': parts[2], 'firmware': parts[3]}

    def reset(self):
        """Resets the instrument (*RST)."""
        self.write("*RST")
        
    def clear_status(self):
        """Clears the status byte and error queue (*CLS)."""
        self.write("*CLS")

    def wait_for_op_complete(self):
        """Waits for all pending operations to complete (*WAI)."""
        self.write("*WAI")

    def get_status_byte(self) -> int:
        """Gets the status byte of the instrument (STB?)."""
        response = self.ask("*STB?")
        return int(response.strip())
    
    # Overload the query method to handle SCPI checks for when the response is ready
    def query(self, command, retries=5, delay=0.5):
        """Send a query command and return the response, with retries for connection errors."""
        attempt = 0
        while attempt < retries:
            try:
                OPC = self._visa_instrument.query("*OPC?")
                time.sleep(delay)
                if int(OPC.strip()) == 1:
                    result = self._visa_instrument.query(command)
                    return result.strip()
                else:
                    pass
                    #raise ConnectionError(f"Instrument not ready for query: {command}")
            except VisaIOError as e:
                print(f"VISA IO Error during query: {e} (attempt {attempt+1}/{retries})")
                attempt += 1
                
        raise ConnectionError(f"Failed to query '{command}' after {retries} attempts due to repeated VISA IO Errors.")