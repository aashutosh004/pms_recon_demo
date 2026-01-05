import pandas as pd

def normalize_bank_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize Bank DataFrame columns to canonical schema:
    txn_date (date)
    ref_no (string)
    amount (numeric)
    dr_cr (string) - inferred or default
    narration (string)
    """
    if df.empty:
        return pd.DataFrame(columns=["txn_date", "ref_no", "amount", "dr_cr", "narration"])
    
    # Ensure columns exist
    required = ["txn_date", "ref_no", "amount", "narration"]
    for col in required:
        if col not in df.columns:
            df[col] = None
            
    # Normalize types
    df['ref_no'] = df['ref_no'].astype(str)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    
    # Infer DR/CR if not present
    # For this specific bank statement, usually lines are Credits (deposits) or Debits (withdrawals).
    # But the raw parser just gives absolute amount.
    # We'll leave dr_cr empty or infer from narration if needed (e.g. "WITHDRAWAL").
    # For now, we'll assume CR (Deposit) if not specified, because we are reconciling against 
    # Broker "Credit" (Receipts). Bank Statement "Credit" = Money In.
    # PROMPT SAYS: "CR = inflow to PMS" (which means Bank Credit).
    if 'dr_cr' not in df.columns:
        df['dr_cr'] = 'CR' # Default assumption for matching against Broker Receipts
        
    return df[["txn_date", "ref_no", "amount", "dr_cr", "narration"]]
