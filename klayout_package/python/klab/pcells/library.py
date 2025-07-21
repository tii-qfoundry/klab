"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
## KLab PCell Library
# This module defines a KLayout library that contains all the PCell definitions as an example
# implementation of a resistance measurement PCell. Klab is designed for this type of definition
# to be distributed as part of the technology specifications, so that klab remains agnostic of the
# setup or process definitions.

import pya

# Import the PCell classes you want to include in the library
from .resistanceMeasurement import ResistanceMeasurement

class KLabPCellLibrary(pya.Library):
    """
    A KLayout library that holds all PCells developed for the KLab package.
    This library is automatically registered with KLayout when the package is loaded.
    """

    def __init__(self):
        # Set the library's name. This is how it will appear in KLayout's library browser.
        self.name = "KLabPCells"
        
        # Set a description for the library
        self.description = "A collection of PCells for instrument control and measurement."

        # --- Register PCells Here ---
        # Use self.layout().register_pcell("cell_name", PCell_class_definition)
        # The "cell_name" is how the PCell will be named inside the library.
        
        self.layout().register_pcell("ResistanceMeasurement", ResistanceMeasurement())
        
        # To add more PCells in the future, just import them and add another
        # self.layout().register_pcell(...) line here.

        # Finally, register this library with the KLayout layout view.
        self.register(self.name)

# Instantiate the library. This is the single entry point that KLayout needs.
if __name__ == "__main__":
    # This will automatically register the library when the script is run.
    KLabPCellLibrary()
