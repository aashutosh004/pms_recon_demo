import streamlit as st
import pandas as pd
import sys
import os
from io import StringIO
import tempfile

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.bank_txt_parser import parse_bank_statement
from parsers.broker_pdf_parser import parse_broker_pdf
from utils.session import init_session

st.set_page_config(page_title="Upload Files", page_icon="📂", layout="wide")

init_session()

st.title("📂 Upload Files")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Bank Statement (TXT)")
    bank_file = st.file_uploader("Upload .TXT File", type=['txt'])
    if bank_file:
        stringio = StringIO(bank_file.getvalue().decode("utf-8"))
        content = stringio.read()
        
        # Show a sneak peek of raw content for debugging
        with st.expander("👀 View Raw File Content (First 500 chars)"):
            st.text(content[:500])
        
        try:
            df = parse_bank_statement(content)
            st.session_state['bank_df'] = df
            
            if df.empty:
                 st.warning("⚠️ File loaded but 0 valid rows parsed. Please check the file format. Expected: 'Date Ref Amount Narration'")
                 st.info("Ensure dates are DD/MM/YYYY and columns are space-separated.")
            else:
                st.success(f"Loaded {len(df)} rows.")
                st.dataframe(df.head(20), use_container_width=True)
                st.info(f"Date Range: {df['txn_date'].min()} to {df['txn_date'].max()}")
                
        except Exception as e:
            st.error(f"Error parsing bank file: {e}")

with col2:
    st.subheader("Broker Ledger (PDF)")
    broker_file = st.file_uploader("Upload .PDF File", type=['pdf'])
    if broker_file:
        # Save to temp file because pdfplumber needs a path (usually)
        # Actually pdfplumber.open can take a file-like object? 
        # Yes, plain file object works.
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(broker_file.getvalue())
                tmp_path = tmp.name
            
            df = parse_broker_pdf(tmp_path)
            st.session_state['broker_df'] = df
            
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass
                
            st.success(f"Loaded {len(df)} rows.")
            st.dataframe(df.head(20), use_container_width=True)
            
            if not df.empty and 'txn_date' in df.columns:
                 # Check if txn_date has valid data
                 valid_dates = df['txn_date'].dropna()
                 if not valid_dates.empty:
                    st.info(f"Date Range: {valid_dates.min()} to {valid_dates.max()}")
        except Exception as e:
            st.error(f"Error parsing broker file: {e}")
            import traceback
            st.write(traceback.format_exc())

st.markdown("---")
if st.session_state.get('bank_df') is not None and st.session_state.get('broker_df') is not None:
    st.success("✅ Both files loaded! Go to **Configuration** or **Reconcile** page.")
