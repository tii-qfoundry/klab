# Example of driver implementation for a SCPI instrument, specifically the 
# Keysight E5080B Network Analyzer, using only parameters specified in a 
# YAML file.

from klab.instrument import SCPIInstrument
import yaml

class KeysightE5080B(SCPIInstrument):   
    """
    Driver for Keysight E5080B Network Analyzer.
    This driver uses parameters defined in a YAML file to configure the instrument.
    """
    def __init__(self, name, address, yaml_path=None, **kwargs):
        super().__init__(name, address, **kwargs)
        self._yaml_path = yaml_path or "tech/driver_keysight_e5080b.yml"
        self._load_yaml_parameters()

    def _load_yaml_parameters(self):
        """Load parameters from the YAML file."""
        try:
            with open(self._yaml_path, 'r') as file:
                self._parameters = yaml.safe_load(file)
            print(f"Loaded parameters from {self._yaml_path}.")
        except FileNotFoundError:
            print(f"YAML file {self._yaml_path} not found. Using default parameters.")
            self._parameters = {}