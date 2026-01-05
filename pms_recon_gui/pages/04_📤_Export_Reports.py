import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Export Reports", page_icon="📤")

st.title("📤 Export Reports")

if 'results' not in st.session_state:
    st.warning("No results found. Please run reconciliation first.")
    st.stop()

res = st.session_state['results']

st.markdown("Download the reconciliation reports below.")

col1, col2 = st.columns(2)

def to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

with col1:
    st.download_button(
        label="Download Matched.csv",
        data=to_csv(res['matched']),
        file_name="matched.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download Partial.csv",
        data=to_csv(res['partial']),
        file_name="partial.csv",
        mime="text/csv",
    )

with col2:
    st.download_button(
        label="Download Unmatched.csv",
        data=to_csv(res['unmatched']),
        file_name="unmatched.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download Exceptions.csv",
        data=to_csv(res['exceptions']),
        file_name="exceptions.csv",
        mime="text/csv",
    )

st.info("Files will be downloaded to your browser's default download location. To save to 'out/' folder automatically, click below (Local Mode Only).")

if st.button("Save All to ./out Folder"):
    out_dir = "out"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    res['matched'].to_csv(f"{out_dir}/matched.csv", index=False)
    res['unmatched'].to_csv(f"{out_dir}/unmatched.csv", index=False)
    res['partial'].to_csv(f"{out_dir}/partial.csv", index=False)
    res['exceptions'].to_csv(f"{out_dir}/exceptions.csv", index=False)
    
    st.success(f"Files saved to {os.path.abspath(out_dir)}")
