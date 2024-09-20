import os
import sys

def add_parent_to_sys_path():
    """Dynamically add the parent directory to sys.path based on the environment."""
    try:
        # Attempt to use __file__ to get the script's directory
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    except NameError:
        # If __file__ is not defined, assume we're in an interactive environment (e.g., Jupyter Notebook)
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)