"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
# Import instrument classes for easy access
from .instruments import KlabInstrument
from .pcells import KLabPCellLibrary


try:
    import pya
except ImportError:
    import klayout.db as pya
    from klayout import ly  # pylint: disable=unused-import