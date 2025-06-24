import functools
import inspect
import yaml
import os

def yaml_method(func):
    """Decorator that marks a method as being implemented in YAML."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Convert positional args to kwargs based on function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())[1:]  # Skip 'self'
        
        for i, arg in enumerate(args):
            if i < len(params):
                kwargs[params[i]] = arg
        
        # Delegate to the YAML implementation
        method_name = func.__name__
        return self._execute_yaml_method(method_name, **kwargs)
        
    wrapper._is_yaml_method = True
    return wrapper

def load_yaml_spec(yaml_file):
    """
    Load an instrument specification from a YAML file.
    It searches first for an absolute path, then for a path relative to the
    package's 'tech' directory.
    """
    # First, try the path as-is (e.g., an absolute path or relative to the current working directory)
    if os.path.isfile(yaml_file):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # If that fails, search relative to the package's 'tech' directory.
    # This avoids a circular import of the 'klab' package.
    try:
        # Get the absolute path to this file (yaml_utils.py)
        this_file_path = os.path.abspath(__file__)
        
        # Navigate up from .../python/klab/instruments/ to the package root
        # that contains the 'python' and 'tech' directories.
        package_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(this_file_path))))
        
        # Construct the full path to the yaml file within the 'tech' directory
        tech_path = os.path.join(package_root, 'tech', yaml_file)
        
        if os.path.isfile(tech_path):
            with open(tech_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception:
        # If path resolution fails for any reason, we'll fall through to the final error.
        pass
        
    raise FileNotFoundError(
        f"Could not find YAML file: '{yaml_file}'. "
        "Searched in the current directory and in the package's 'tech' directory."
    )