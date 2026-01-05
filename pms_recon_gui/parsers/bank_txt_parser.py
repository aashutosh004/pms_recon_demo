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
    # Could be "478322208/12390"
    raw_ref = parts[1]
    ref_no = clean_ref_no(raw_ref)
    
    # 3. Amount (Token 2)
    # Could be "1,046,729.56" (includes commas)
    raw_amt = parts[2]
    try:
        amount = float(raw_amt.replace(',', ''))
    except ValueError:
        # If amount parsing fails, maybe the structure is off
        return None
    
    # 4. Narration (Rest)
    narration = " ".join(parts[3:])
    
    # 5. Infer DR/CR? 
    # The requirement says "Amount ... CR = inflow to PMS, DR = outflow"
    # But text file just has absolute amount usually.
    # We will assume absolute amount for now.
    # Logic might differ if there is a DR/CR flag effectively in the text, 
    # but the sample line doesn't show it.
    # We will look for keywords in narration if needed, or just keep it absolute.
    
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
