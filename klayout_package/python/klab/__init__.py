"""
klab - A Python package for KLayout integration with lab instrumentation.

This package provides tools and utilities to enhance and automate instrument control in KLayout,
a popular layout viewer and editor for integrated circuits.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
# Import instrument classes for easy access
from .instruments.klab_instrument import KlabInstrument
from .pcells import KLabPCellLibrary
