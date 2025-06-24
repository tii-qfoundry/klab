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

# Set envormnemnt variable KLAB_DEBUG_STREAM to true
os.environ['KLAB_DEBUG_STREAM'] = 'False'

from klab.instruments import Keithley2450
from klab.instruments.scpi_instrument import NoQuote

# --- Setup ---
# IMPORTANT: Replace with the actual VISA address of your instrument
VISA_ADDRESS = 'TCPIP0::192.168.0.95::INSTR' # Example: 'TCPIP0::192.168.1.123::INSTR'

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
    smu.source_current(current=1e-5, voltage_compliance=0.1)
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
    error_message = smu.syst.err()
    print(f"  > Last error message: {error_message}")
    print("-" * 30)

    # === Hybrid Method: Setup from YAML, parsing in Python ===
    # The `measure_resistance` method calls `set_resistance` from the YAML file,
    # then call the `read_measurement(count)`, alsoi defined .
    print("4. Calling a hybrid method (`measure_voltage`)...")
    resistance = smu.meas_resistance(current=1e-5, 
                                     voltage_compliance=0.1, 
                                     count=10)

    print(f"  > Final measured resistance trace, mode 1: {resistance}")
    print("-" * 30)

    # Equivalent to 

    smu.source_current(current=1e-5, voltage_compliance=0.1)
    smu.sens.volt.unit(NoQuote('Ohm'))
    smu.sens.volt.ocom(NoQuote('ON'))
    resistance = smu.run_measurement(count=10)

    print(f"  > Final measured resistance trace, mode 2: {resistance}")
    print("-" * 30)


    # --- Clean up ---
    print("Example complete. Closing connection.")
    smu.close()
