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
    """Load an instrument specification from a YAML file."""
    # First try absolute path
    if os.path.isfile(yaml_file):
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    # Then try relative to klab/tech directory
    try:
        import klab
        base_dir = os.path.dirname(os.path.dirname(klab.__file__))
        tech_path = os.path.join(base_dir, 'tech', yaml_file)
        
        if os.path.isfile(tech_path):
            with open(tech_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            base_dir = os.path.dirname(base_dir)
            tech_path = os.path.join(base_dir, 'tech', yaml_file)
            if os.path.isfile(tech_path):
                with open(tech_path, 'r') as f:
                    return yaml.safe_load(f)
    except:
        pass
        
    raise FileNotFoundError(f"Could not find YAML file: {yaml_file}")