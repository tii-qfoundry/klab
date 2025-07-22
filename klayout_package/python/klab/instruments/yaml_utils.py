"""
klab - A Python package for KLayout integration with lab instrumentation.

Copyright (c) 2025, Technology Innovation Institute. All rights reserved.

"""
import functools
import inspect
import yaml
import os

def yaml_method(func):
    """
    A decorator that marks a method as requiring an implementation in a YAML file.

    This decorator is used in abstract base classes or other instrument
    drivers to enforce that a concrete implementation provides a corresponding
    method definition in its associated YAML specification.

    If a method decorated with `@yaml_method` does not have a corresponding
    entry in the YAML file's `methods` section, a `NotImplementedError`
    is raised during instrument initialization.

    Example:
        In an abstract class:
        ```python
        @yaml_method
        def measure_resistance(self, **kwargs):
            # This will be implemented in YAML
            return self._execute_yaml_method('measure_resistance', **kwargs)
        ```
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Convert positional args to kwargs based on function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()

        # The first argument is 'self', so we skip it.
        all_kwargs = {k: v for k, v in bound_args.arguments.items() if k != 'self'}

        # The actual execution is handled by the instrument's YAML method runner
        return self._execute_yaml_method(func.__name__, **all_kwargs)
    
    wrapper._is_yaml_method = True
    return wrapper

def load_yaml_spec(file_path: str) -> dict:
    """
    Loads an instrument's command specification from a YAML file.

    This function is responsible for finding and parsing the YAML file that
    defines an instrument's high-level methods. It searches for the file
    relative to the calling module's path and in the current working directory.

    Args:
        file_path (str): The name or relative path of the YAML file.

    Returns:
        dict: The parsed YAML content as a Python dictionary.

    Raises:
        FileNotFoundError: If the YAML file cannot be found.
    """
    # Get the directory of the file that called this function
    caller_frame = inspect.stack()[1]
    caller_path = os.path.dirname(os.path.abspath(caller_frame.filename))

    # List of paths to check for the YAML file
    search_paths = [
        os.path.join(caller_path, file_path),  # Relative to the caller's module
        file_path,                             # Relative to the current working directory
    ]

    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
    
    raise FileNotFoundError(f"Could not find the YAML specification file '{file_path}' in any of the search paths.")