import pya
import sys
import os
import subprocess
import importlib
import shutil

# This script implements the strategy of using an external, clean virtual
# environment to drive the installation of packages into KLayout's
# user-specific site-packages directory.

# --- VENV AND PACKAGE CONFIGURATION ---
VENV_DIR_NAME = ".klab_venv"  # Name of the venv to create within the package
PACKAGE_NAME = "klab"         # For user-facing messages

# Map package names to the name they are imported by, for special cases.
IMPORT_NAME_MAP = {
    "pyvisa-py": "pyvisa_py",
}

def parse_requirements(req_path):
    """
    Parses a requirements.txt file to yield package specifications.
    Requires 'packaging' to be installed in the venv.
    """
    from packaging.requirements import Requirement
    with open(req_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                yield Requirement(line)

def setup_klab_venv(package_root, klayout_py_version_str):
    """
    Creates a dedicated virtual environment to get a reliable pip executable.

    This function requires a python interpreter (matching KLayout's version if possible)
    to be available on the system's PATH.

    Args:
        package_root (str): The root directory of the klab salt package.
        klayout_py_version_str (str): Python version string like "3.11".

    Returns:
        str: The absolute path to the pip executable in the new venv, or None on failure.
    """
    venv_path = os.path.join(package_root, VENV_DIR_NAME)
    
    # Determine the path to pip inside the venv
    pip_exe_name = "pip.exe" if sys.platform == "win32" else "pip"
    venv_pip_path = os.path.join(venv_path, "Scripts" if sys.platform == "win32" else "bin", pip_exe_name)

    # If the venv and its pip already exist, we are done.
    if os.path.isfile(venv_pip_path):
        print(f"Found existing klab virtual environment at: {venv_path}")
        return venv_pip_path
    
    print(f"Creating new klab virtual environment at: {venv_path}...")
    
    # Find a python executable on the system path
    python_exe = shutil.which(f"python{klayout_py_version_str}") or shutil.which("python3") or shutil.which("python")
    
    if not python_exe:
        error_msg = ("Could not find a Python interpreter on the system's PATH.\n\n"
                     f"This is now required to create a helper environment for installing packages.\n"
                     "Please install Python or ensure its location is in your PATH environment variable.")
        print(f"ERROR: {error_msg}")
        pya.MessageBox.critical("Fatal Installation Error", error_msg, pya.MessageBox.Ok)
        return None

    print(f"Found system Python at: {python_exe}. Creating venv...")
    
    try:
        command = [python_exe, "-m", "venv", venv_path]
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully created virtual environment.")
        return venv_pip_path
    except subprocess.CalledProcessError as e:
        error_msg = (f"Failed to create the virtual environment using '{python_exe}'.\n\n"
                     f"--- Stderr ---\n{e.stderr}")
        print(f"ERROR: {error_msg}")
        pya.MessageBox.critical("Fatal Installation Error", error_msg, pya.MessageBox.Ok)
        return None

def check_and_install_dependencies(pip_executable, target_dir):
    """
    Checks for required Python packages and installs them into the target directory.
    
    Args:
        pip_executable (str): Path to the reliable pip from our venv.
        target_dir (str): The KLayout site-packages directory to install into.

    Returns:
        bool: True if all dependencies are met, False otherwise.
    """
    print(f"Checking for required Python packages for {PACKAGE_NAME}...")

    # First, use the reliable pip to ensure 'packaging' is in the venv itself
    try:
        subprocess.run([pip_executable, "install", "packaging"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pya.MessageBox.warning("Installation Warning", "Could not install 'packaging' in helper venv.", pya.MessageBox.Ok)
        # This might not be fatal if it was already there.
    
    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    reqs_file = os.path.join(package_root, 'requirements.txt')
    if not os.path.exists(reqs_file):
        pya.MessageBox.warning("Installation Error", "Could not find requirements.txt.", pya.MessageBox.Ok)
        return False

    all_installed = True
    for req in parse_requirements(reqs_file):
        module = IMPORT_NAME_MAP.get(req.name, req.name.replace('-', '_'))
        try:
            # We check for installation in the *current* environment, which should
            # have access to the target_dir path.
            importlib.import_module(module)
            print(f"- Dependency '{req.name}' is already installed.")
        except ImportError:
            print(f"- Dependency '{req.name}' not found. Attempting install...")
            try:
                command = [pip_executable, "install", "--target", target_dir, str(req)]

                print(f"  > Running command: {' '.join(command)}")
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)

                print(f"- Successfully installed '{req.name}'.")
                # We may need to reload modules if they were just installed
                try:
                    importlib.import_module(module)
                except ImportError:
                    print(f"  > Warning: '{req.name}' was installed but could not be imported. "
                          "This may indicate a problem with the installation.") 
            except (subprocess.CalledProcessError, ImportError) as e:
                stdout_info = f"--- Stdout ---\n{e.stdout}\n" if hasattr(e, 'stdout') and e.stdout else ""
                stderr_info = f"--- Stderr ---\n{e.stderr}\n" if hasattr(e, 'stderr') and e.stderr else ""
                error_msg = (f"Failed to install '{req.name}' into target directory.\n\n" f"{stdout_info}{stderr_info}")
                print(f"ERROR: {error_msg}")
                pya.MessageBox.warning("Dependency Installation Failed", error_msg, pya.MessageBox.Ok)
                all_installed = False


    return all_installed

def install():
    """
    This function is called by KLayout to install the plugin.
    """
    klayout_py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # 1. Determine the correct KLayout site-packages directory as the target
    # This is the most reliable way to find the user's script/package folder.
    app_data_path = pya.Application.instance().application_data_path()
    target_site_packages = os.path.join(app_data_path, "lib", f"python{klayout_py_version}", "site-packages")
    os.makedirs(target_site_packages, exist_ok=True)
    
    # Add this to the path if it's not there, so imports can be found.
    if target_site_packages not in sys.path:
        sys.path.insert(0, target_site_packages)

    # 2. Set up the virtual environment to get a reliable pip
    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pip_executable = setup_klab_venv(package_root, klayout_py_version)
    if not pip_executable:
        print(f"Halting {PACKAGE_NAME} installation due to venv setup failure.")
        return

    # 3. Use the reliable pip to install dependencies into the target directory
    if not check_and_install_dependencies(pip_executable, target_site_packages):
        print(f"Halting {PACKAGE_NAME} installation due to missing dependencies.")
        return

    # 4. Register the menu
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
