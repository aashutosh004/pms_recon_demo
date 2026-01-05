import streamlit as st
import yaml
from pathlib import Path

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="PMS Recon Tool",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_config():
    """Load configuration from config.yml"""
    config_path = Path("config.yml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

def main():
    st.title("🏦 Bank ↔ Broker Reconciliation")
    st.markdown("### Welcome to the Local Reconciliation Tool")
    
    # Initialize session state for data storage
    if 'bank_df' not in st.session_state:
        st.session_state['bank_df'] = None
    if 'broker_df' not in st.session_state:
        st.session_state['broker_df'] = None
    if 'config' not in st.session_state:
        st.session_state['config'] = load_config()

    st.info("👈 Please start by uploading files in the **Upload Files** page.")
    
    st.markdown("""
    #### Workflow:
    1. **Upload Files**: Load Bank Statement (.txt) and Broker Ledger (.pdf)
    2. **Configuration**: Adjust date windows and tolerances.
    3. **Reconcile**: Run the matching engine.
    4. **Export**: Download matched/unmatched reports.
    """)

if __name__ == "__main__":
    main()
