import pandas as pd
from typing import List, Dict, Any, Optional
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.dates import parse_date
from utils.refs import clean_ref_no

def parse_bank_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single line from the bank text file.
    Expected format: 
    Date       Ref                Amount        Narration
    28/08/2025 478322208/12390    1,046,729.56  BNKFT-PMS PMS-CIPS
    """
    parts = line.strip().split()
    if len(parts) < 3:
        return None
    
    # 1. Date (Token 0)
    date_val = parse_date(parts[0])
    if not date_val:
        return None # Not a valid line
    
    # 2. Reference (Token 1)
    raw_ref = parts[1]
    ref_no = clean_ref_no(raw_ref)
    
    # 3. Amount (Token 2)
    # Check if token 2 is amount. If not, maybe token 1 was part of date? No.
    # Maybe Extra spaces?
    raw_amt = parts[2]
    amount = 0.0
    try:
        amount = float(raw_amt.replace(',', ''))
    except ValueError:
        # Retry with Token 3 if Token 2 was something else?
        # But per requirements: Date Ref Amount.
        # Let's be strict for now, or returns None to skip header.
        return None
    
    # 4. Narration (Rest)
    narration = " ".join(parts[3:])
    
    return {
        "txn_date": date_val,
        "ref_no": ref_no,
        "amount": amount,
        "narration": narration,
        "raw_line": line.strip()
    }

def parse_bank_statement(file_content: str) -> pd.DataFrame:
    """
    Parses the content of a Bank TXT file.
    Returns a tuple: (DataFrame, debug_info_dict)
    But to keep signature simple, we might just return DF, 
    but for debugging we need more info if it's empty.
    
    Let's change this to return clean DF, 
    but we will print to stderr or log if possible?
    
    Actually, let's allow it to return just DF, but we will make it try harder.
    """
    lines = file_content.splitlines()
    data = []
    
    for line in lines:
        if not line.strip():
            continue
            
        parsed = parse_bank_line(line)
        if parsed:
            data.append(parsed)
            
    df = pd.DataFrame(data)
    if not df.empty:
        # Ensure correct types
        df['txn_date'] = pd.to_datetime(df['txn_date']).dt.date
        df['amount'] = df['amount'].astype(float)
        df['ref_no'] = df['ref_no'].astype(str)
        
    return df
