import pandas as pd
import argparse
import sys
import os
import re

# Add src to path
sys.path.append(os.path.dirname(__file__))

from text_rules import clean_particulars

def clean_amount(val):
    if pd.isna(val):
        return 0.0
    s = str(val).strip()
    # Remove "+ " prefix
    s = s.replace('+ ', '').replace('+', '')
    # Remove commas
    s = s.replace(',', '')
    # Handle negative in parens (100) -> -100 (if applicable)
    if '(' in s and ')' in s:
        s = '-' + s.replace('(', '').replace(')', '')
    try:
        return float(s)
    except:
        return 0.0

def process_broker_csv(input_path, output_path):
    print(f"Reading {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Normalize Columns
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Ensure canonical columns exist
    # Mapping might be needed if source CSV has different names
    # Assuming source has: transaction_date, particulars, flow strings etc based on user prompt?
    # User prompt says source is "already parsed to CSV".
    # Let's verify columns or be robust.
    
    # 1. Dates (YYYY-MM-DD)
    if 'txn_date' in df.columns:
        df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # 2. Amounts
    if 'debit' in df.columns:
        df['debit'] = df['debit'].apply(clean_amount)
    if 'credit' in df.columns:
        df['credit'] = df['credit'].apply(clean_amount)
        
    # 3. Particulars & Bank Ref Extraction
    if 'particulars' in df.columns:
        df['particulars'] = df['particulars'].apply(clean_particulars)
        
        # New Column: bank_ref_in_particulars
        # Regex: Reference No.\s*:\s*([A-Za-z0-9]+)
        def extract_bank_ref(text):
            if not isinstance(text, str): return None
            m = re.search(r'(?:Reference|Ref)\.?\s*No\.?\s*[:\-]\s*([A-Za-z0-9]+)', text, re.IGNORECASE)
            if m:
                return m.group(1)
            return None
            
        df['bank_ref_in_particulars'] = df['particulars'].apply(extract_bank_ref)
        
    # 4. Ref (Standardize)
    if 'transaction_ref' in df.columns:
        df['transaction_ref'] = df['transaction_ref'].fillna('').astype(str).str.strip()
        
    # Output
    print(f"Writing to {output_path}...")
    df.to_csv(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_file", required=True)
    parser.add_argument("--out", dest="output_file", required=True)
    args = parser.parse_args()
    
    process_broker_csv(args.input_file, args.output_file)
