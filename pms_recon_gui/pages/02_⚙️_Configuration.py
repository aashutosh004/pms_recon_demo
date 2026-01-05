import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.session import init_session

st.set_page_config(page_title="Configuration", page_icon="⚙️")

# Initialize session (handles config loading)
init_session()

st.title("⚙️ Configuration")

if 'config' not in st.session_state:
    st.error("Could not load configuration file.")
    st.stop()

config = st.session_state['config']

st.header("Matching Rules")

st.subheader("📅 Date Window")
date_window = st.number_input(
    "Allowed Date Difference (Days)", 
    min_value=0, max_value=30, 
    value=config.get('date_window_days', 2)
)

st.subheader("🔍 Fuzzy Matching")
sim_enabled = st.checkbox("Enable Similarity Matching", value=config.get('similarity_enabled', True))
sim_threshold = st.slider(
    "Similarity Threshold", 
    min_value=0.5, max_value=1.0, 
    value=config.get('similarity_threshold', 0.85),
    step=0.01
)

st.header("💰 Tolerance Settings")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### IPS Charge Range (NPR)")
    ips_min = st.number_input("Min", value=config.get('tolerance', {}).get('ips_min', 2.0))
    ips_max = st.number_input("Max", value=config.get('tolerance', {}).get('ips_max', 10.0))

with col2:
    st.markdown("#### RTGS Threshold")
    rtgs_threshold = st.number_input("RTGS Amount Threshold", value=config.get('tolerance', {}).get('rtgs_threshold', 2000000.0))
    rtgs_flat = st.number_input("Flat Tolerance (NPR)", value=config.get('tolerance', {}).get('rtgs_flat', 100.0))

# Save button logic (implicit in session state update)
if st.button("Save Configuration", type="primary"):
    new_config = config.copy()
    new_config['date_window_days'] = date_window
    new_config['similarity_enabled'] = sim_enabled
    new_config['similarity_threshold'] = sim_threshold
    
    if 'tolerance' not in new_config:
        new_config['tolerance'] = {}
    new_config['tolerance']['ips_min'] = ips_min
    new_config['tolerance']['ips_max'] = ips_max
    new_config['tolerance']['rtgs_threshold'] = rtgs_threshold
    new_config['tolerance']['rtgs_flat'] = rtgs_flat
    
    st.session_state['config'] = new_config
    st.success("Configuration updated for this session!")
    st.json(new_config)
