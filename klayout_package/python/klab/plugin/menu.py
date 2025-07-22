# ==================================================================
# FILE: klab/python/klab/plugin/menu.py
# ==================================================================
# This script is responsible for creating the "Measurement" menu in
# the KLayout main window and connecting its actions to placeholder
# functions.
# ==================================================================

try:
    import pya
except ImportError:
    # pya module is not available (likely running outside KLayout)
    import klayout.db as pya

import sys
import os

# Add the parent directory to the system path to allow for relative imports
# Note: KLayout's Salt manager should handle this, but this is a fallback.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the MeasurementDock class from the easurementDock.py file
from  klab.plugin.measurementDock import MeasurementDock
from importlib import reload
import klab.plugin.measurementDock


measurement_dock_instance = None

def register_klab_menu():
    """
    Creates and registers the 'Measurement' menu in the KLayout main window.

    This function sets up the main entry point for the klab plugin in the
    KLayout user interface. It adds a "Measurement" menu with the following
    actions:
        - "Show Measurement Tab": Shows or hides the MeasurementDock.
        - "Refresh Measurement Tab": Reloads and re-registers the dock.
        - "Run Measurement": Triggers a measurement on the selected PCell.
    """
    app = pya.Application.instance()
    mw = app.main_window()

    # --- Create Menu if it doesn't exist ---
    if not mw.menu().find_menu('klab_menu'):
        menu = mw.menu().insert_menu('klab_menu', "Measurement")
    else:
        menu = mw.menu().find_menu('klab_menu')

    # --- Action: Show/Hide Measurement Tab ---
    action_show = pya.QAction("Show Measurement Tab", mw)
    action_show.triggered(toggle_measurement_dock)
    menu.add_action(action_show)

    # --- Action: Refresh Measurement Tab ---
    action_refresh = pya.QAction("Refresh Measurement Tab", mw)
    action_refresh.triggered(refresh_measurement_dock)
    menu.add_action(action_refresh)

    # --- Action: Run Measurement ---
    action_run = pya.QAction("Run Measurement", mw)
    action_run.triggered(run_measurement_on_selected)
    menu.add_action(action_run)

def toggle_measurement_dock():
    """
    Shows or hides the MeasurementDock widget.

    If the dock does not exist, it creates a new instance. If it is
    visible, it hides it, and if it is hidden, it shows it.
    """
    global measurement_dock_instance
    if measurement_dock_instance is None:
        measurement_dock_instance = MeasurementDock(pya.Application.instance().main_window())
    
    if measurement_dock_instance.is_visible():
        measurement_dock_instance.hide()
    else:
        measurement_dock_instance.show()
        pya.Application.instance().main_window().addDockWidget(pya.Qt.RightDockWidgetArea, measurement_dock_instance)

def refresh_measurement_dock():
    """

    Reloads and re-registers the MeasurementDock.

    This function is useful for development, allowing UI and logic changes
    to be applied without restarting KLayout. It reloads the
    `measurementDock` module and creates a new instance of the dock.
    """
    global measurement_dock_instance
    if measurement_dock_instance:
        measurement_dock_instance.hide()
        del measurement_dock_instance
        measurement_dock_instance = None
    
    # Reload the module and create a new instance
    reload(klab.plugin.measurementDock)
    from klab.plugin.measurementDock import MeasurementDock
    measurement_dock_instance = MeasurementDock(pya.Application.instance().main_window())
    measurement_dock_instance.show()
    pya.Application.instance().main_window().addDockWidget(pya.Qt.RightDockWidgetArea, measurement_dock_instance)
    print("MeasurementDock has been refreshed.")

def run_measurement_on_selected():
    """
    Triggers the measurement on the currently selected PCell.

    This function provides a menu-driven way to execute a measurement,
    calling the `run_measurement` method of the active MeasurementDock
    instance.
    """
    global measurement_dock_instance
    if measurement_dock_instance:
        measurement_dock_instance.run_measurement()
    else:
        pya.Application.instance().main_window().message("Measurement tab is not active.", 2000)

# This is the single entry point called by Ruby at startup.
def setup_plugin():
    refresh_measurement_dock()

