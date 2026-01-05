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
    # We pass the full text as "narration context" to help decision making (e.g. check for "Tax")
    ref_no = extract_ref(other_tokens, full_text)
    
    # Narration: Join other tokens, excluding the Ref
    # Also exclude tokens that look like the ref we just found (to clean up narration)
    
    final_tokens = []
    for t in other_tokens:
        # If t is exactly the ref or starts with ref (if ref is long)
        if ref_no and (t == ref_no or (len(ref_no) > 5 and t.startswith(ref_no))):
            continue
        # Also clean up "Interest" specific noise if needed?
        # User said: "Interest (12/08/25-17/10/25)" -> Keep it.
        # User said: "IPS CHARGE ... remove trailing Dr/Cr totals" -> The Dr/Cr totals likely look like "1,673,000.48".
        # We already filtered out "valid amounts" into `amounts`. 
        # But 'valid_amounts' logic was: "abs(a) > 0.001".
        # If the balance line "1,673,000.48" was in `amounts`, it's gon.
        # If it wasn't valid amount (maybe formatting?), it's here.
        
        final_tokens.append(t)

    narration = clean_narration(" ".join(final_tokens))
    
    # Ref cleanup (stripping /prefix) inside extract_ref logic? 
    # extract_ref logic usually returns the Clean token if it matched the split logic.
    # But if it matched "CDS-...", it returns "CDS-..."
    # If extract_ref returned "47832208", then t "47832208/1230" wouldn't match "47832208" EXACTLY.
    # We need to handle that in the loop above.
    
    # Re-loop to catch the original token that *generated* the ref_no
    if ref_no:
        final_tokens_2 = []
        for t in other_tokens:
            # Check if t "contains" ref_no or vice versa?
            # t: "47832208/1230", ref_no: "47832208"
            if str(ref_no) in t and len(str(ref_no)) > 5:
                continue
            if t == str(ref_no):
                continue
            final_tokens_2.append(t)
        narration = clean_narration(" ".join(final_tokens_2))
    
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
