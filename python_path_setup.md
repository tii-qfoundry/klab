# Adding klab to Python Path - Multiple Methods

This guide shows different ways to add the klab package to your Python path depending on your use case.

## Current Project Structure
```
klab/
├── klayout_package/
│   ├── python/
│   │   └── klab/           # ← This is what needs to be in Python path
│   │       ├── __init__.py
│   │       └── instruments/
│   └── examples/
│       └── example_SMU.py  # ← Your current file
```

## Method 1: Runtime Path Addition (Script-Level)

**Use case**: For individual scripts or when you don't want to modify system settings

```python
import sys
import os

# Add klab package to Python path for this script only
klab_python_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python'))
if klab_python_path not in sys.path:
    sys.path.insert(0, klab_python_path)

# Now you can import klab
from klab.instruments.drivers.keithley_2450 import Keithley2450
```

## Method 2: Environment Variable (Session-Level)

**Use case**: For all Python scripts in your current terminal/IDE session

### Windows (PowerShell)
```powershell
# Set for current session
$env:PYTHONPATH = "C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python;$env:PYTHONPATH"

# Or permanently for your user
[Environment]::SetEnvironmentVariable("PYTHONPATH", "C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python", "User")
```

### Windows (Command Prompt)
```cmd
# Set for current session
set PYTHONPATH=C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python;%PYTHONPATH%

# Or permanently
setx PYTHONPATH "C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python;%PYTHONPATH%"
```

### Linux/Mac
```bash
# Add to current session
export PYTHONPATH="/path/to/klab/klayout_package/python:$PYTHONPATH"

# Add to ~/.bashrc or ~/.profile for permanent
echo 'export PYTHONPATH="/path/to/klab/klayout_package/python:$PYTHONPATH"' >> ~/.bashrc
```

## Method 3: Development Installation (Recommended for Development)

**Use case**: When actively developing klab or using it frequently

### Create a setup.py file in the klab/klayout_package/python directory:

```python
# File: klab/klayout_package/python/setup.py
from setuptools import setup, find_packages

setup(
    name="klab",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "pyvisa",
        "pyyaml",
    ],
    python_requires=">=3.7",
)
```

### Then install in development mode:
```bash
cd C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python
pip install -e .
```

This creates a link to your development folder, so changes are immediately available.

## Method 4: VS Code / IDE Configuration

**Use case**: For development in VS Code or other IDEs

### VS Code settings.json:
```json
{
    "python.analysis.extraPaths": [
        "C:/Users/juan.villegas/Documents/Github/klab/klayout_package/python"
    ],
    "python.defaultInterpreterPath": "path/to/your/python.exe"
}
```

### PyCharm:
1. File → Settings → Project → Python Interpreter
2. Click gear icon → Show All
3. Select your interpreter → Show paths for selected interpreter
4. Add path: `C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python`

## Method 5: Virtual Environment with Path

**Use case**: Isolated development environment

```bash
# Create virtual environment
python -m venv klab_env

# Activate it
# Windows:
klab_env\Scripts\activate
# Linux/Mac:
source klab_env/bin/activate

# Add path to site-packages
echo "C:\Users\juan.villegas\Documents\Github\klab\klayout_package\python" > klab_env\Lib\site-packages\klab.pth
```

## Method 6: For KLayout Environment

**Use case**: When running within KLayout's embedded Python

```python
# Add to your KLayout Python scripts
import sys
import os

# KLayout-specific path addition
klayout_klab_path = os.path.join(os.path.dirname(__file__), 'python')
if klayout_klab_path not in sys.path:
    sys.path.insert(0, klayout_klab_path)
```

## Verification Script

Use this to test if klab is properly accessible:

```python
#!/usr/bin/env python3
"""Test script to verify klab import"""

def test_klab_import():
    try:
        import sys
        print("Python path includes:")
        for i, path in enumerate(sys.path):
            if 'klab' in path.lower():
                print(f"  {i}: {path} ✓")
        
        print("\nTesting imports...")
        
        # Test basic import
        import klab
        print(f"✓ klab imported from: {getattr(klab, '__file__', 'unknown')}")
        
        # Test specific modules
        from klab.instruments.abstract_classes import SMU, VNA, MotorStage
        print("✓ Abstract classes imported successfully")
        
        from klab.instruments.klab_instrument import KlabInstrument
        print("✓ KlabInstrument imported successfully")
        
        from klab.instruments.drivers.keithley_2450 import Keithley2450
        print("✓ Keithley2450 driver imported successfully")
        
        print("\n🎉 All imports successful! klab is properly configured.")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that the path is correct")
        print("2. Verify klab/klayout_package/python/klab/__init__.py exists")
        print("3. Try Method 1 (runtime path addition) for immediate testing")
        return False
    
    return True

if __name__ == "__main__":
    test_klab_import()
```

## Recommendation

For your current situation, I'd recommend:

1. **Short term**: Use Method 1 (runtime path addition) - it's what you're already doing
2. **Long term**: Use Method 3 (development installation) for easier management
3. **For KLayout**: Use Method 6 when running within KLayout

The runtime path addition you're currently using is perfect for examples and testing!
