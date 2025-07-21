"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.
"""
## 
# Example of driver implementation for a SCPI instrument, specifically the 
# Keysight E5080B Network Analyzer, using only parameters specified in a 
# YAML file.

from ..scpi_instrument import ScpiInstrument

class KeysightE5080B(ScpiInstrument):   
    """
    Driver for Keysight E5080B Network Analyzer.
    This driver uses parameters defined in a YAML file to configure the instrument.
    """
    def __init__(self, name, address, yaml_path=None, **kwargs):
        super().__init__(name, address, **kwargs)
        self._yaml_path = yaml_path or "tech/driver_keysight_e5080b.yml"
        self._load_yaml_parameters()

    