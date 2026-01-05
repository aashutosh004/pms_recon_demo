import streamlit as st
import yaml
from pathlib import Path
import os
import sys

# Ensure root path is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

def load_config():
    """Load configuration from config.yml"""
    # Try different paths depending on where the script is run
    paths_to_try = [
        Path("config.yml"),
        Path("../config.yml"),
        Path(os.path.join(root_dir, "config.yml"))
    ]
    
    for config_path in paths_to_try:
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
    return {}

def init_session():
    """Initialize session state variables if they don't exist."""
    if 'config' not in st.session_state or not st.session_state['config']:
        st.session_state['config'] = load_config()
        
    if 'bank_df' not in st.session_state:
        st.session_state['bank_df'] = None
        
    if 'broker_df' not in st.session_state:
        st.session_state['broker_df'] = None
        
    if 'results' not in st.session_state:
        st.session_state['results'] = None
