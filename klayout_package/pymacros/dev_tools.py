import sys
import importlib
# Import the menu module so we can call its refresh function
from klab.plugin import menu as plugin_menu

def reload_klab_package():
    """
    Finds and reloads all modules associated with the 'klab' package,
    then refreshes the UI elements like the measurement dock.
    """
    print("--- Starting KLab Package Reload ---")
    
    package_name = "klab"
    
    modules_to_reload = [
        name for name, module in sys.modules.items() 
        if name.startswith(package_name) and module is not None
    ]
    
    if not modules_to_reload:
        print("No 'klab' modules found in sys.modules. Nothing to reload.")
        return
        
    print(f"Found {len(modules_to_reload)} modules to reload...")
    
    # Reload all the python modules first
    for module_name in sorted(modules_to_reload, key=lambda n: n.count('.'), reverse=True):
        try:
            print(f"  Reloading: {module_name}")
            importlib.reload(sys.modules[module_name])
        except Exception as e:
            print(f"    ERROR reloading {module_name}: {e}")
            
    print("--- Python modules reloaded ---")
    
    # --- This is the crucial step ---
    # After reloading the code, explicitly refresh the UI.
    print("Refreshing KLab UI elements...")
    plugin_menu.refresh_measurement_dock()
    
    print("--- KLab Package Reload Complete ---")