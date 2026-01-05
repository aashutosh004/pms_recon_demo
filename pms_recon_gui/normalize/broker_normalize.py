import pandas as pd

def normalize_broker_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize Broker DataFrame columns to canonical schema:
    txn_date (date)
    transaction_ref (string)
    credit (numeric)
    debit (numeric)
    particulars (string)
    settlement_date (date)
    """
    if df.empty:
        cols = ["txn_date", "transaction_ref", "credit", "debit", "particulars", "settlement_date"]
        return pd.DataFrame(columns=cols)

    # Ensure columns exist
    required = ["txn_date", "transaction_ref", "credit", "debit", "particulars"]
    for col in required:
        if col not in df.columns:
            if col in ['credit', 'debit']:
                df[col] = 0.0
            else:
                df[col] = None
                
    if 'settlement_date' not in df.columns:
        df['settlement_date'] = df['txn_date']
        
    # Clean types
    df['transaction_ref'] = df['transaction_ref'].astype(str).str.strip()
    df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0.0)
    df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0.0)
    
    return df[["txn_date", "transaction_ref", "credit", "debit", "particulars", "settlement_date"]]
