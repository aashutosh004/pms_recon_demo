import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from normalize.bank_normalize import normalize_bank_data
from normalize.broker_normalize import normalize_broker_data
from engine.matcher import Matcher

st.set_page_config(page_title="Reconcile", page_icon="✅", layout="wide")

st.title("✅ Run Reconciliation")

if st.session_state.get('bank_df') is None or st.session_state.get('broker_df') is None:
    st.error("Missing Data! Please upload files in Page 01.")
    st.stop()

if st.button("🚀 Run Reconciliation Process", type="primary"):
    with st.spinner("Normalizing data..."):
        bank_norm = normalize_bank_data(st.session_state['bank_df'])
        broker_norm = normalize_broker_data(st.session_state['broker_df'])
        
    with st.spinner("Matching records..."):
        matcher = Matcher(bank_norm, broker_norm, st.session_state.get('config', {}))
        results = matcher.run()
        st.session_state['results'] = results
        st.success("Reconciliation Complete!")

if 'results' in st.session_state:
    res = st.session_state['results']
    matched = res['matched']
    unmatched = res['unmatched']
    partial = res['partial']
    exceptions = res['exceptions']
    
    # KPIs
    st.divider()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Matched Rows", len(matched))
    k2.metric("Unmatched Rows", len(unmatched), delta_color="inverse")
    k3.metric("Partial Matches", len(partial), delta_color="off")
    k4.metric("Exceptions", len(exceptions), delta_color="inverse")
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Matched", "Unmatched", "Partial", "Exceptions"])
    
    with tab1:
        st.dataframe(matched, use_container_width=True)
    
    with tab2:
        st.dataframe(unmatched, use_container_width=True)
        
    with tab3:
        st.dataframe(partial, use_container_width=True)
        
    with tab4:
        st.dataframe(exceptions, use_container_width=True)
