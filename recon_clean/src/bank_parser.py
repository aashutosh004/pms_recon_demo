import argparse
import sys
import os
import re
import csv
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(__file__))

from regex_utils import DATE_PATTERN, AMOUNT_PATTERN
from text_rules import is_noise_line
from ref_rules import extract_ref, clean_narration

def parse_bank_txi(input_path, output_path):
    print(f"Parsing Bank TXI: {input_path}...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    cleaned_rows = []
    
    # State machine variables
    current_date = None
    current_lines = [] # To merge split lines
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 1. Noise Filter
        if is_noise_line(line):
            continue
            
        # 2. Date Detection (Start of Transaction)
        # Regex for line starting with date: "21/11/2025 ..."
        date_match = DATE_PATTERN.match(line)
        
        if date_match and len(line) < 80 and "Summary" not in line: 
             # It's a start of a new transaction
             
             # Process previous cluster if exists
             if current_lines:
                 row = process_transaction_cluster(current_lines)
                 if row: cleaned_rows.append(row)
                 current_lines = []
             
             current_lines.append(line)
        else:
            # Continuation line?
            # If no current cluster, maybe it's garbage before first txn
            if current_lines:
                current_lines.append(line)
            else:
                 pass # Ignore header garbage
                 
    # Process last cluster
    if current_lines:
        row = process_transaction_cluster(current_lines)
        if row: cleaned_rows.append(row)
        
    # Write to CSV
    print(f"Writing {len(cleaned_rows)} rows to {output_path}...")
    keys = ["txn_date", "ref_no", "amount", "narration"]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    print("Done.")

def process_transaction_cluster(lines):
    """
    Merge lines for a single transaction.
    Example split dividend:
    Line 1: 21/11/2025 1,594.00 0.00
    Line 2: 1,594.00 CD
    
    Strategy: Join all text, then parse tokens.
    """
    full_text = " ".join(lines)
    tokens = full_text.split()
    
    # 1. Extract Date
    # First token usually
    raw_date = tokens[0]
    try:
        dt = datetime.strptime(raw_date, "%d/%m/%Y")
        txn_date = dt.strftime("%Y-%m-%d")
    except:
        return None # Invalid cluster
        
    # 2. Extract Amount
    # Usually the Amount is numeric.
    # In Bank Stmt: Date <Ref?> <Amount> ...
    # Or Date <Amount> ... 
    # Let's look for numeric tokens that are regex-matched as amount.
    
    amounts = []
    other_tokens = []
    
    # Skip date
    for t in tokens[1:]:
        # Remove commas for check
        clean_t = t.replace(',', '')
        if re.match(r'^[\-\+]?\d+(\.\d{2})?$', clean_t):
            amounts.append(float(clean_t))
        else:
            other_tokens.append(t)
            
    # Heuristic: The largest absolute value is usually the transaction amount?
    # Or strict position?
    # Bank stmt usually has Debit / Credit columns.
    # If TXI collapses them, we might get multiple numbers (0.00, 1594.00, etc)
    # The requirement says "1,594.00 0.00 1,594.00".
    # We want the non-zero one.
    
    valid_amounts = [a for a in amounts if abs(a) > 0.001]
    amount = valid_amounts[0] if valid_amounts else 0.0
    
    # 3. Extract Ref & Narration
    # Use helper rules
    ref_no = extract_ref(other_tokens, full_text)
    
    # Narration: Join other tokens, excluding the Ref
    # And exclude Date/Amount tokens which we handled specifically?
    # Actually just filtering out recognized Ref is usually safer.
    
    narration_tokens = [t for t in other_tokens if t != ref_no]
    narration = clean_narration(" ".join(narration_tokens))
    
    # Ref cleanup (stripping /prefix)
    # The extract_ref logic handles some of this, but let's be sure.
    if '/' in str(ref_no) and len(str(ref_no)) > 10: 
        # e.g. 47832208/1230 -> 47832208
        # Assuming the second part is suffix
        ref_no = str(ref_no).split('/')[0]
        
    return {
        "txn_date": txn_date,
        "ref_no": ref_no,
        "amount": amount,
        "narration": narration
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_file", required=True)
    parser.add_argument("--out", dest="output_file", required=True)
    args = parser.parse_args()
    
    parse_bank_txi(args.input_file, args.output_file)
