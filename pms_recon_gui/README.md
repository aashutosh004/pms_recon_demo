# PMS Reconciliation Tool (Local GUI)

A Streamlit-based application for reconciling Bank Statements with Broker Ledgers.

## Features
- **Bank Parsing**: Custom parser for plain text bank statements.
- **Broker Parsing**: PDF table extraction for broker ledgers.
- **Reconciliation Engine**:
    - Date window matching (±2 days).
    - Amount tolerance handling (IPS charges, RTGS).
    - Fuzzy matching options.
- **Interactive UI**: Dashboard, Drill-downs, and CSV exports.

## Setup & Running

1. **Create Virtual Environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

4. **Usage**:
   - Navigate to **"01 📂 Upload Files"** to load data.
   - Configure rules in **"02 ⚙️ Configuration"**.
   - Run process in **"03 ✅ Reconcile"**.
   - Download results from **"04 📤 Export Reports"**.

## Input Data
Place sample files in `data/` for quick access:
- `bishal_yakha_bank_statement.TXT`
- `Bishal_Yakha_Broker_Ledger.pdf`
