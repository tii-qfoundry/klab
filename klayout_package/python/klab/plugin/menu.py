import pya
import sys
import os

# Add the parent directory to the system path to allow for relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .measurement_tab import MeasurementDock

class MeasurementMenu(pya.QObject):
    """
    Manages the 'Measurement' menu in the KLayout main window.
    This class is responsible for creating the menu and handling its actions.
    """
    def __init__(self, window):
        super(MeasurementMenu, self).__init__()
        self.window = window
        self.menu_name = "&Measurement"
        self.menu = self.window.menu().insert_menu(self.menu_name, -1)
        self.measurement_dock = None

        # Add initial actions to the menu
        self.create_action("Setup Measurement", self.setup_measurement)
        self.create_action("Run Measurement", self.run_measurement)
        
    def create_action(self, text, slot):
        """Helper function to create a QAction and add it to the menu."""
        action = pya.QAction(text, self.window)
        action.triggered(slot)
        self.menu.add_action(action)

    def setup_measurement(self):
        """
        Action to open the measurement setup tab.
        """
        if not self.measurement_dock:
            self.measurement_dock = MeasurementDock(self.window)
            self.window.addDockWidget(pya.Qt.RightDockWidgetArea, self.measurement_dock)
        self.measurement_dock.show()
        pya.Logger.info("Measurement setup activated.")

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

