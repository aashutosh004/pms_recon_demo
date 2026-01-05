import pandas as pd
import re
from typing import List, Dict, Any, Optional
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.dates import parse_date
from utils.refs import clean_ref_no

def is_start_line(line: str) -> bool:
    """
    Check if a line marks the start of a transaction.
    Pattern: Index + Date (e.g., "2    28/08/2025 ...")
    """
    # Regex: Start with optional space, digits, space, date(dd/mm/yyyy)
    return bool(re.match(r'^\s*\d+\s+\d{2}/\d{2}/\d{4}', line))

def extract_amount(line: str) -> Optional[float]:
    """Extract amount from the end of the line"""
    tokens = line.strip().split()
    if not tokens:
        return None
    
    # Try the last token first (common case)
    try:
        val = float(tokens[-1].replace(',', ''))
        return val
    except ValueError:
        pass
    
    # Try second to last (if there's trailing garbage?)
    # But usually it's the last.
    return None

def find_ref_candidate(tokens: List[str]) -> Optional[str]:
    """
    Look for a reference-like token in the list.
    Priority:
    1. Contains '/' and digits (e.g., 478322208/12390)
    2. Long sequence of digits (e.g., 72012511010096CZ or just digits)
    3. CDS pattern (CDS-xxxx)
    """
    for t in tokens:
        # Case 1: Slash Ref
        if '/' in t and any(c.isdigit() for c in t):
            return t
        
        # Case 3: CDS
        if t.startswith('CDS-'):
            return t
            
    # Case 2: Long alphanumeric (mostly digits)
    # Filter out common non-ref words?
    for t in tokens:
        if len(t) > 6 and any(c.isdigit() for c in t) and '/' not in t:
             # Basic heuristic: if it has digits and length > 6, likely a ref
             # Excluding dates (handled elsewhere usually)
             if not re.match(r'\d{2}/\d{2}/\d{4}', t):
                 return t
                 
    return None

def parse_bank_block(block_lines: List[str]) -> Optional[Dict[str, Any]]:
    """
    Parse a multiline block representing one transaction.
    Line 0 is the Header line.
    """
    if not block_lines:
        return None
    
    header = block_lines[0]
    tokens = header.strip().split()
    
    # 1. Date (Token 1 typically, Token 0 is Index)
    # Pattern: "2 28/08/2025 ..."
    if len(tokens) < 2:
        return None
        
    date_val = parse_date(tokens[1])
    if not date_val:
        # Fallback: maybe Index is huge or missing? Check Token 0
        date_val = parse_date(tokens[0])
        
    if not date_val:
        return None # Can't identify date
        
    # 2. Amount (Last token of header)
    amount = extract_amount(header)
    if amount is None:
        amount = 0.0 # Should flag error?
        
    # 3. Reference & Narration
    # We scan all tokens in Header (excluding Index, Date, Amount) 
    # AND all tokens in sub-lines.
    
    all_text_tokens = []
    
    # Header text (skip index, date, amount)
    # Index=0, Date=1. Amount=Last.
    # Be careful with indices.
    header_content = tokens[2:-1] if len(tokens) > 3 else [] 
    all_text_tokens.extend(header_content)
    
    # Sublines
    for line in block_lines[1:]:
        sub_tokens = line.strip().split()
        if sub_tokens:
             # Check if this line is just a "summary" or "~Date" noise?
             # User image has "~Date" or "summary"
             if "~Date" in line or "summary" in line:
                 continue
             all_text_tokens.extend(sub_tokens)
             
    # Strategy: Find best Ref token, rest is Narration.
    ref_token = find_ref_candidate(all_text_tokens)
    
    # If Ref found, remove it from text to form narration?
    # Or keep it in narration too? Usually harmless.
    
    narration_parts = [t for t in all_text_tokens if t != ref_token]
    narration = " ".join(narration_parts)
    
    # Clean ref
    ref_no = clean_ref_no(ref_token) if ref_token else "UNKNOWN"
    
    return {
        "txn_date": date_val,
        "ref_no": ref_no,
        "amount": amount,
        "narration": narration,
        "raw_line": header # Store main line for reference
    }

def parse_bank_statement(file_content: str) -> pd.DataFrame:
    """
    Parses the content of a Bank TXT file (Block-based).
    """
    lines = file_content.splitlines()
    blocks = []
    current_block = []
    
    for line in lines:
        if not line.strip():
            continue
            
        if is_start_line(line):
            # Finish previous block
            if current_block:
                blocks.append(current_block)
            # Start new block
            current_block = [line]
        else:
            # Append to current block (if active)
            if current_block:
                current_block.append(line)
                
    # Append last block
    if current_block:
        blocks.append(current_block)
        
    # Process blocks
    data = []
    for block in blocks:
        parsed = parse_bank_block(block)
        if parsed:
            data.append(parsed)
            
    df = pd.DataFrame(data)
    if not df.empty:
        df['txn_date'] = pd.to_datetime(df['txn_date']).dt.date
        df['amount'] = df['amount'].astype(float)
        df['ref_no'] = df['ref_no'].astype(str)
        
    return df
