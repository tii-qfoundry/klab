# ==================================================================
# FILE: klab/python/klab/plugin/menu.py
# ==================================================================
# This script is responsible for creating the "Measurement" menu in
# the KLayout main window and connecting its actions to placeholder
# functions.
# ==================================================================

import pya
import sys
import os

# Add the parent directory to the system path to allow for relative imports
# Note: KLayout's Salt manager should handle this, but this is a fallback.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the MeasurementDock class from the measurement_tab.py file
from klab.plugin.measurement_tab import MeasurementDock

class MeasurementMenu(pya.QObject):
    """
    Manages the 'Measurement' menu in the KLayout main window.
    This class is responsible for creating the menu and handling its actions.
    """
    def __init__(self, window):
        super(MeasurementMenu, self).__init__()
        self.window = window
        self.menu_name = "&Measurement"
        self.menu = self.window.menu().insert_menu(".help", "klab_menu", self.menu_name)
        self.measurement_dock = None

        # Add initial actions to the menu
        self.create_action("Setup Measurement", self.setup_measurement)
        self.create_action("Run Measurement", self.run_measurement)
        
    def create_action(self, text, slot):
        """Helper function to create a QAction and add it to the menu."""
        action = pya.QAction(text, self.window)
        action.triggered(slot)
        #self.menu.addAction(action)

    def setup_measurement(self):
        """
        Action to open the measurement setup tab. This now creates and
        shows the dockable widget.
        """
        if self.measurement_dock is None:
            # Create an instance of our custom dock widget
            self.measurement_dock = MeasurementDock(self.window)
            # Add it to the main window, docked on the right
            self.window.addDockWidget(pya.Qt.RightDockWidgetArea, self.measurement_dock)
        
        # Ensure the dock is visible
        self.measurement_dock.show()
        pya.Logger.info("Measurement dock shown.")


    def run_measurement(self):
        """
        Placeholder for the action to run a measurement.
        """
        pya.Logger.info("Running measurement...")
        # Later, this will trigger the measurement runner.
        pya.MessageBox.info("Info", "Measurement run initiated (placeholder).", pya.MessageBox.Ok)

# Global instance of the menu handler
measurement_menu_handler = None

def register_menu(window):
    """
    Function to be called by KLayout to register the menu.
    """
    global measurement_menu_handler
    if measurement_menu_handler is None:
        measurement_menu_handler = MeasurementMenu(window)


if __name__ == "__main__":
    """
    This block is for testing the menu in a standalone script.
    It will not run when KLayout loads this module.
    """
    app = pya.Application.instance()
    main_window = app.main_window()

    # Register the menu
    register_menu(main_window)

    # Show the main window to test the menu
    main_window.show()
    
    # Start the application event loop
    #app.exec_()
