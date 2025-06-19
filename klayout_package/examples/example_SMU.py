# ==================================================================
# This script demonstrates the three ways to interact with the klab
# hybrid instrument driver for the Keithley 2450.
# ==================================================================

# Make sure the klab package is in the Python path
import sys
import os
import time

# This adds the parent directory of 'klab' to the path,
# assuming the file structure is klab/examples/example_keithley_usage.py
# and the package is at klab/python/klab
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python'))
sys.path.insert(0, package_path)


from klab.drivers.keithley_2450 import Keithley2450

# --- Setup ---
# IMPORTANT: Replace with the actual VISA address of your instrument
VISA_ADDRESS = 'TCPIP0::192.168.1.95::INSTR' # Example: 'TCPIP0::192.168.1.123::INSTR'

# Create an instance of the driver
print(f"Attempting to connect to Keithley 2450 at {VISA_ADDRESS}...")
smu = Keithley2450(name='my_keithley_smu', address=VISA_ADDRESS)

# Check if the connection was successful before proceeding
if smu._visa_instrument is None:
    print("\nCould not connect to instrument. Exiting example.")
else:
    print("\n--- Demonstrating Different Method Types ---\n")

    # === Method 1: Explicitly defined in the Python driver ===
    # This method has clear documentation and logic defined directly in keithley_2450.py
    print("1. Calling a method explicitly defined in the Python driver (`set_average_count`)...")
    smu.set_average_count('VOLT', 10)
    print("-" * 30)

    # === Method 2: Dynamically executed from the YAML file ===
    # The 'set_current' method is not implemented in the Python file.
    # It calls `_execute_yaml_method` which runs the 'source_current' sequence from the YAML.
    print("2. Calling a method that executes a sequence from the YAML file (`set_current`)...")
    smu.set_current(current=1e-5, voltage_compliance=0.1)
    # The `enable_source` method also works this way.
    smu.enable_source(enable=True)
    time.sleep(0.5)
    smu.enable_source(enable=False)
    print("-" * 30)

    # === Method 3: Dynamically generated on-the-fly by the SCPI Proxy ===
    # The methods 'system', 'beeper', and 'get_error' do not exist anywhere in our code.
    # The __getattr__ proxy intercepts these calls and builds the SCPI command automatically.
    print("3. Calling methods dynamically via the SCPI proxy (`system.beeper`)...")
    # This sends the command: :SYST:BEEP 500, 1
    smu.system.beeper(500, 1) 
    
    # You can also use this for queries. This sends `:SYST:ERR?`
    error_message = smu.get_error()
    print("-" * 30)

    # === Hybrid Method: Setup from YAML, parsing in Python ===
    # The `measure_voltage` method calls `setup_measure_voltage` from the YAML file,
    # then performs the read and data parsing in Python.
    print("4. Calling a hybrid method (`measure_voltage`)...")
    smu.source_voltage(voltage=0.1, current_compliance=0.01)
    smu.enable_source(enable=True)
    time.sleep(0.5)
    measured_voltage = smu.measure_voltage(nplc=1)
    smu.enable_source(enable=False)
    print(f"  > Final measured voltage: {measured_voltage} V")
    print("-" * 30)


    # --- Clean up ---
    print("Example complete. Closing connection.")
    smu.close()
