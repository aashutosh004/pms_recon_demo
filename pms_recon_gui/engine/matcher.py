import pandas as pd
import uuid
from typing import List, Dict, Any
from .rules import within_date_window, compute_tolerance, check_similarity
from .exceptions import ExceptionCode, ReconException

class Matcher:
    def __init__(self, bank_df: pd.DataFrame, broker_df: pd.DataFrame, config: dict):
        self.bank_df = bank_df
        self.broker_df = broker_df
        self.config = config
        
        self.matches = []
        self.unmatched = []
        self.partial = []
        self.exceptions = []
        
        self.matched_broker_indices = set()
        
    def run(self):
        """
        Execute Matching Logic.
        """
        date_window = self.config.get('date_window_days', 2)
        similarity_enabled = self.config.get('similarity_enabled', False)
        sim_threshold = self.config.get('similarity_threshold', 0.85)
        
        # Iterate over Bank rows
        for b_idx, bank_row in self.bank_df.iterrows():
            bank_date = bank_row['txn_date']
            bank_ref = bank_row['ref_no']
            bank_amt = abs(bank_row['amount'])
            bank_narration = bank_row['narration']
            
            # Calculate dynamic tolerance for this row
            tolerance = compute_tolerance(bank_amt, bank_narration, self.config)
            
            # 1. Filter Candidates (Date Window)
            # We filter broker_df where index not used and date in window
            # (Optimization: Can be vectorised, but loop is fine for local tool)
            
            candidates = []
            
            for br_idx, broker_row in self.broker_df.iterrows():
                if br_idx in self.matched_broker_indices:
                    continue
                
                br_date = broker_row['txn_date'] or bank_date # Fallback if missing?
                
                if within_date_window(bank_date, br_date, date_window):
                    candidates.append((br_idx, broker_row))
            
            match_found = False
            best_match = None
            match_type = None
            
            # 2. Try EXACT Match (Ref + Amount)
            for cid, crow in candidates:
                crow_credit = abs(crow['credit'])
                # Check Amount with tiny tolerance (float precision) or configured tolerance?
                # Usually "Exact" means 0 diff, but we allow tolerance generally.
                amt_diff = abs(bank_amt - crow_credit)
                
                # Check Ref
                # Exact string match
                ref_match = (str(bank_ref) == str(crow['transaction_ref']))
                
                if ref_match and amt_diff <= tolerance:
                    best_match = (cid, crow)
                    match_type = 'EXACT'
                    break
            
            # 3. Fallback 1: Amount Match (Ref mismatch)
            if not best_match:
                # Find candidates with matching amount
                # Prefer closest date?
                potential_amts = []
                for cid, crow in candidates:
                    crow_credit = abs(crow['credit'])
                    amt_diff = abs(bank_amt - crow_credit)
                    
                    if amt_diff <= tolerance:
                        potential_amts.append((cid, crow))
                
                if len(potential_amts) == 1:
                    # Single candidate with matching amount -> Valid Match (Ref Mismatch Exception/Warning)
                    best_match = potential_amts[0]
                    # Check if ref is totally different or just fuzzy?
                    match_type = 'REF_MISMATCH'
                elif len(potential_amts) > 1:
                    # Multiple matching amounts -> Ambiguous
                    # We skip mapping for now and mark as ambiguous exception?
                    # Or try fuzzy ref match to break tie
                    pass
            
            # 4. Fallback 2: Simpson/Fuzzy Match (if enabled)
            if not best_match and similarity_enabled:
                best_score = 0
                temp_match = None
                
                for cid, crow in candidates:
                    # Check similarity of Ref or Narration vs Particulars
                    score_ref = 0
                    if bank_ref and crow['transaction_ref']:
                        if check_similarity(bank_ref, crow['transaction_ref'], sim_threshold):
                            score_ref = 1.0 # High confidence
                            
                    score_narr = 0
                    if check_similarity(bank_narration, crow['particulars'], sim_threshold):
                        score_narr = 1.0
                        
                    if score_ref or score_narr:
                        # Check amount? Usually must be close.
                        # If amount is way off, fuzzy match shouldn't count?
                        # Let's enforce amount tolerance even for fuzzy match
                        crow_credit = abs(crow['credit'])
                        amt_diff = abs(bank_amt - crow_credit)
                        
                        if amt_diff <= tolerance:
                            temp_match = (cid, crow)
                            break # Take first good fuzzy match
                
                if temp_match:
                    best_match = temp_match
                    match_type = 'FUZZY'

            # Finalize Row
            if best_match:
                br_idx, crow = best_match
                self.matched_broker_indices.add(br_idx)
                
                match_entry = {
                    "match_id": str(uuid.uuid4()),
                    "bank_row_id": b_idx,
                    "broker_row_id": br_idx,
                    "date": bank_date,
                    "bank_amount": bank_amt,
                    "broker_credit": crow['credit'],
                    "delta": bank_amt - crow['credit'],
                    "match_type": match_type,
                    "bank_ref": bank_ref,
                    "broker_ref": crow['transaction_ref']
                }
                
                if match_type == 'REF_MISMATCH':
                    # Log exception/warning but considered "Matched" or "Partial"?
                    # Prompt says "Partial (with note ref mismatch)".
                    # We'll put it in Matched but flag it, or Partial list?
                    # Let's put in Partial.
                    self.partial.append({
                        **match_entry,
                        "note": "Amount matched, Ref mismatch"
                    })
                    # Add exception record
                    self.exceptions.append({
                        "code": ExceptionCode.REF_MISMATCH,
                        "description": f"Ref mismatch: {bank_ref} != {crow['transaction_ref']}",
                        "bank_ref": bank_ref,
                        "broker_ref": crow['transaction_ref']
                    })
                else:
                    self.matches.append(match_entry)

            else:
                # No match found
                self.unmatched.append({
                    "bank_row_id": b_idx,
                    "date": bank_date,
                    "amount": bank_amt,
                    "ref": bank_ref,
                    "reason": "No matching candidate found in window/tolerance"
                })
        
        # Post-loop: Find Unmatched Broker Rows
        for br_idx, broker_row in self.broker_df.iterrows():
            if br_idx not in self.matched_broker_indices:
                # Only care about Credit rows?
                # Broker Ledger has Debit and Credit. 
                # Reconciling Bank (Money In/Out) matches Broker (Money Out/In).
                # Bank Debit (Out) ~ Broker Debit (Purchase)?
                # Bank Credit (In) ~ Broker Credit (Receipt)?
                
                # Prompt says: "Bank ↔ Broker matching rules... abs(bank.amount - broker.credit) <= tolerance"
                # This implies we are primarily reconciling Bank Amounts (Inflow?) against Broker Credits (Receipts).
                # If the broker row is a 'Debit' (Purchase), it might correspond to a Bank Debit.
                # But the prompt focuses on "Received in BANK ... Reference No.".
                # If it's a Credit row in Broker and not matched -> Unmatched
                if broker_row['credit'] > 0:
                     self.unmatched.append({
                        "broker_row_id": br_idx,
                        "date": broker_row['txn_date'],
                        "amount": broker_row['credit'],
                        "ref": broker_row['transaction_ref'],
                        "reason": "Broker Credit not found in Bank"
                    })
        
        return {
            "matched": pd.DataFrame(self.matches),
            "unmatched": pd.DataFrame(self.unmatched),
            "partial": pd.DataFrame(self.partial),
            "exceptions": pd.DataFrame(self.exceptions)
        }
