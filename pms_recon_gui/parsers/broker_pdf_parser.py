import pdfplumber
import pandas as pd
import re
import sys
import os
from typing import Optional

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.dates import parse_date

def normalize_pdf_table_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attempt to find the header row and set it.
    Looking for columns like 'Date', 'Particulars', 'Debit', 'Credit'.
    """
    # Simply look for a row containing "Particulars" or "Debit"
    for i, row in df.iterrows():
        row_str = " ".join([str(x) for x in row.values]).lower()
        if "particulars" in row_str and ("debit" in row_str or "credit" in row_str):
            # This is likely the header
            df.columns = df.iloc[i]
            df = df.iloc[i+1:].reset_index(drop=True)
            return df
    return df

def extract_ref_from_particulars(particulars: str) -> Optional[str]:
    """
    Extract reference number from particulars text.
    Example: "Received in BANK ... Reference No.: 478322208"
    """
    if not isinstance(particulars, str):
        return None
        
    # Pattern: "Reference No.: <digits>" or "Ref No : <digits>"
    match = re.search(r'Ref(?:erence)?\.?\s*No\.?\s*[:\-]\s*(\w+)', particulars, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def parse_broker_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Parse Broker PDF using pdfplumber.
    """
    rows = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # Convert to DF for easier processing validation
                df_chunk = pd.DataFrame(table)
                # We won't normalize every chunk individually immediately
                # Instead we just collect valid-looking rows
                # But table structure might vary. 
                # Strategy: Append raw rows, clean later?
                # Better: Try to identify columns by index if standard.
                
                # Heuristic: Broker ledger usually has 5 columns:
                # [Transaction Reference Number, Particulars, Debit, Credit, Balance]
                # Sometimes Date is separate.
                # Let's clean the row data.
                
                for row in table:
                    # Clean None/Empty
                    clean_row = [str(cell).replace('\n', ' ').strip() if cell else '' for cell in row]
                    rows.append(clean_row)

    # Convert all gathered rows to DataFrame
    df = pd.DataFrame(rows)
    
    # Normalize headers
    df = normalize_pdf_table_headers(df)
    
    # Standardize column names
    # Map common variations to canonical names
    # Expected: "Date", "Particulars", "Debit", "Credit", "Reference"
    # Actually the prompt says: "Transaction Reference Number / Particulars / Debit / Credit / Balance"
    
    # Simple column mapping based on keyword matching
    new_cols = {}
    print(f"DEBUG: Found Raw Columns: {df.columns.tolist()}") # Debug print for server logs
    
    for col in df.columns:
        c = str(col).lower().strip()
        # Map "Transaction" or "Date" to txn_date
        # Use loose 'in' matching logic
        if ('date' in c) or ('transac' in c):
             new_cols[col] = 'txn_date'
        elif 'particular' in c:
            new_cols[col] = 'particulars'
        elif 'debit' in c:
            new_cols[col] = 'debit'
        elif 'credit' in c:
            new_cols[col] = 'credit'
        # Map "Reference Number", "Ref No", "Transaction Ref", or just "Reference"
        elif 'ref' in c: 
            new_cols[col] = 'transaction_ref'
    
    df.rename(columns=new_cols, inplace=True)
    
    # Post-processing
    final_data = []
    
    for idx, row in df.iterrows():
        # Skip header repetition or empty
        if 'particulars' not in row or not row['particulars']:
            continue
            
        # Parse Amount
        # Credit/Debit might be strings with commas
        credit = 0.0
        debit = 0.0
        
        if 'credit' in row and row['credit']:
            try:
                credit = float(str(row['credit']).replace(',', ''))
            except: pass
            
        if 'debit' in row and row['debit']:
            try:
                debit = float(str(row['debit']).replace(',', ''))
            except: pass
            
        # Parse Date
        txn_date = None
        if 'txn_date' in row:
            txn_date = parse_date(str(row['txn_date']))
            
        # Extract Reference from Particulars if column not present/empty
        # Or if we want to augment "transaction_ref" with what's in particulars
        # The prompt says: "Received in BANK ... Reference No.: 478322208"
        
        particulars = str(row['particulars'])
        extracted_ref = extract_ref_from_particulars(particulars)
        
        # Use extracted ref if explicit column is missing or empty
        ref_val = None
        if 'transaction_ref' in row and row['transaction_ref']:
             ref_val = str(row['transaction_ref']).strip()
        
        if not ref_val and extracted_ref:
            ref_val = extracted_ref
            
        # Add to list
        # Filter out rows that are just headers or junk
        if not txn_date and credit == 0 and debit == 0:
            continue
            
        final_data.append({
            "txn_date": txn_date,
            "transaction_ref": ref_val,
            "particulars": particulars,
            "debit": debit,
            "credit": credit
        })
        
    res_df = pd.DataFrame(final_data)
    # Filter rows with no meaningful amount
    res_df = res_df[(res_df['debit'] != 0) | (res_df['credit'] != 0)]
    
    return res_df
