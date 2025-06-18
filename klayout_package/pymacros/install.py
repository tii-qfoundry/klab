import pya
import sys
import os
import subprocess
import importlib
import shutil
from importlib.metadata import version as get_version
from packaging.version import Version

# This script implements the strategy of calling pip's internal main function
# to install packages into KLayout's user site-packages directory.

# --- VENV AND PACKAGE CONFIGURATION ---
PACKAGE_NAME = "klab"                       # For user-facing messages

# Map package names to the name they are imported by, for special cases.
IMPORT_NAME_MAP = {
    "pyvisa-py": "pyvisa_py",
    "rpds-py": "rpds",
}

def get_pip_main():
    """
    Imports and returns the main function from pip, handling different
    versions of pip where the location of _main might change.
    """
    try:
        from pip import __main__
        if hasattr(__main__, "_main"):
            return __main__._main
        else:
            # Fallback for older pip versions
            from pip._internal.cli.main import main
            return main
    except ImportError as e:
        pya.MessageBox.critical("Fatal Installation Error", f"Could not import pip's main function. Your KLayout Python environment may have a broken pip installation.\n\nError: {e}", pya.MessageBox.Ok)
        return None

def _get_klayout_python_info():
    """
    Gathers key platform and version info about KLayout's Python environment
    to help pip resolve the correct binary wheels.
    """
    from packaging.tags import sys_tags
    info = {
        'version': f"{sys.version_info.major}.{sys.version_info.minor}",
        'platforms': [str(tag) for tag in sys_tags()]
    }
    return info

def parse_requirements(req_path):
    """
    Parses a requirements.txt file to yield package specifications.
    Requires 'packaging' to be installed.
    """
    from packaging.requirements import Requirement
    with open(req_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                yield Requirement(line)

def check_and_install_dependencies(pip_main, target_dir):
    """
    Checks for required Python packages and their versions, and installs them 
    into the target directory by calling pip's main function directly.
    
    Args:
        pip_main (function): The main function from the pip module.
        target_dir (str): The KLayout user site-packages directory to install into.

    Returns:
        bool: True if all dependencies are met, False otherwise.
    """
    print(f"Checking for required Python packages for {PACKAGE_NAME}...")

    # First, ensure 'packaging' is installed, as it's needed for parsing.
    try:
        importlib.import_module("packaging")
    except ImportError:
        print("- 'packaging' library not found. Installing it first...")
        try:
            # We don't need platform info for packaging itself, as it's pure python.
            command = ["install", "--upgrade", "--target", target_dir, "--no-build-isolation", "--only-binary=:all:", "packaging"]
            retcode = pip_main(command)
            if retcode != 0:
                raise RuntimeError(f"pip failed with exit code {retcode}")
            importlib.import_module("packaging")
        except Exception as e:
            pya.MessageBox.warning("Installation Error", f"Could not install the 'packaging' library. klab cannot continue.\n\nError: {e}", pya.MessageBox.Ok)
            return False

    # Now that 'packaging' is installed, we can get environment info.
    py_info = _get_klayout_python_info()

    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    reqs_file = os.path.join(package_root, 'requirements.txt')
    if not os.path.exists(reqs_file):
        pya.MessageBox.warning("Installation Error", "Could not find requirements.txt.", pya.MessageBox.Ok)
        return False

    all_installed = True
    missing_dependencies = []
    for req in parse_requirements(reqs_file):
        module_name = IMPORT_NAME_MAP.get(req.name, req.name.replace('-', '_'))
        try:
            # Check if module can be imported.
            importlib.import_module(module_name)
            installed_version_str = get_version(module_name)
            
            if req.specifier.contains(installed_version_str):
                print(f"- Dependency '{req.name}' (v{installed_version_str}) is already installed and compatible.")
            else:
                print(f"- Dependency '{req.name}' (v{installed_version_str}) is installed but incompatible with '{req.specifier}'. Will upgrade.")
                raise ImportError("Version mismatch")

        except (ImportError, importlib.metadata.PackageNotFoundError):
            print(f"- Dependency '{req.name}' not found or incompatible. Installing directly via pip API...")
            try:
                # --- KEY CHANGE: Loop through platforms and try to install one by one ---
                install_success = False
                last_error_code = -1
                
                # Base command that is the same for all attempts
                base_command = ["install", "--upgrade", "--target", target_dir, "--no-build-isolation", "--only-binary=:all:"]
                if  sys.platform.startswith('win'):
                    # On Windows, we use --no-deps to avoid issues with binary wheels.
                    # This is because KLayout's Python environment may not have all dependencies installed.
                    base_command.append("--no-deps")
                    
                    # Use --force-reinstall to ensure we get the correct version.
                    base_command.append("--force-reinstall")
                else:
                    # On non-Windows platforms, we allow pip to resolve dependencies.
                    pass
                
                # Attempt to install for each platform in the KLayout Python environment, until one succeeds.
                print(f"  > KLayout Python version: {py_info['version']}")
                for plat in py_info['platforms']:
                    command = list(base_command) # Create a copy
                    command.extend(["--python-version", py_info['version']])
                    command.extend(["--platform", plat])
                    # no cache if its the first install attempt
                    if last_error_code != -1:
                        command.append("--no-cache-dir")
                    command.append(str(req))

                    # Call pip's main function with the command
                    print(f"  > Attempting install with platform '{plat}'...")

                    # Use the pip main function to execute the command
                    # Note: pip_main expects a list of arguments, not a string.
                    retcode = pip_main(command)
                    if retcode == 0:
                        install_success = True
                        break # Exit the loop on first success
                    else:
                        last_error_code = retcode
                
                if not install_success:
                    raise RuntimeError(f"pip failed to install '{req.name}' for all compatible platforms. Last exit code: {last_error_code}")

                print(f"- Successfully installed/upgraded '{req.name}'.")
                
                importlib.invalidate_caches()
                # Try to load the module, if there is a module missing error, it will be caught below.
                try:
                    # Import the module to ensure it was installed correctly.
                    # This is important for binary packages that may not have been imported before.
                    if module_name in sys.modules:
                        del sys.modules[module_name]  # Clear cache if it was already loaded
                    importlib.import_module(module_name)
                except ImportError as e:
                    error_msg = f"Module '{module_name}' was installed but could not be imported. This may indicate a binary compatibility issue.\n\n"
                    # If there is a missing module error, add it to the dependency list.
                    # This will allow the user to see which module is missing.

                    if 'No module named' in e.args[0]: 
                        print(f"ERROR: {error_msg}Additional dependency '{e.name}' is missing after installation.")
                        if e.name not in missing_dependencies:
                            missing_dependencies.append(e.name)
                    else:
                        print(f"ERROR: {error_msg}{e}")
                    all_installed = False

            except (RuntimeError, ImportError) as e:
                error_msg = f"Failed to install '{req.name}'.\n\n{e}"   
                print(f"ERROR: {error_msg}")
                pya.MessageBox.warning("Dependency Installation Failed", error_msg, pya.MessageBox.Ok)
                all_installed = False
                missing_dependencies.append(req.name)
    
    if not all_installed:
        print(f"Some dependencies for {PACKAGE_NAME} could not be installed:")
        for dep in missing_dependencies:
            print(f"- {dep}")
    return all_installed

def install():
    """
    This function is called by KLayout to install the plugin.
    """
    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the main klab python source directory to the path, just in case.
    klab_python_dir = os.path.join(package_root, 'python')
    if klab_python_dir not in sys.path:
        sys.path.insert(0, klab_python_dir)
        print(f"Added main package source directory to Python path: {klab_python_dir}")
    
    # Determine the KLayout user site-packages directory as the target.
    klayout_py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    app_data_path = pya.Application.instance().application_data_path()
    target_dir = os.path.join(app_data_path, "lib", f"python{klayout_py_version}", "site-packages")
    os.makedirs(target_dir, exist_ok=True)
    
    # Add this directory to Python's path to ensure it's available.
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
        print(f"Added KLayout user site-packages directory to Python path: {target_dir}")

    # Set KLAYOUT_PYTHONHOME if it is not already defined.
    if 'KLAYOUT_PYTHONHOME' not in os.environ:
        os.environ['KLAYOUT_PYTHONHOME'] = target_dir
        print(f"Set KLAYOUT_PYTHONHOME environment variable to: {target_dir}")

    # Get pip's main function to drive the installation.
    pip_main_func = get_pip_main()
    if not pip_main_func:
        print(f"Halting {PACKAGE_NAME} installation due to missing pip function.")
        return

    # Use the reliable pip function to install dependencies into the KLayout user site-packages.
    if not check_and_install_dependencies(pip_main_func, target_dir):
        print(f"Halting {PACKAGE_NAME} installation due to missing dependencies.")
        return

    # Register the menu.
    try:
        from klab.plugin.menu import register_menu
        main_window = pya.Application.instance().main_window()
        register_menu(main_window)
        print(f"{PACKAGE_NAME} package loaded successfully.")
    except Exception as e:
        print(f"An error occurred while loading the {PACKAGE_NAME} package: {e}")
        import traceback
        traceback.print_exc()

# Execute the installation when KLayout loads this macro.
install()
