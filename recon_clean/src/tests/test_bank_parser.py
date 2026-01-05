import pytest
import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ref_rules import extract_ref, clean_narration
from bank_parser import process_transaction_cluster

def test_interest_row_fix():
    # User Case: "2025-10-17 5,659.06 12 Interest (12/08/25-17/10/25)" 
    # The "12" is a ref candidate but should be ignored.
    lines = ["17/10/2025 5,659.06 12", "Interest (12/08/25-17/10/25)"]
    row = process_transaction_cluster(lines)
    assert row['ref_no'] == "" or row['ref_no'] is None
    assert row['amount'] == 5659.06
    assert "Interest" in row['narration']

def test_tax_row_fix():
    # User Case: "Tax for 06411701339531000001"
    lines = ["17/10/2025 339.54", "Tax for 06411701339531000001"]
    row = process_transaction_cluster(lines)
    assert row['ref_no'] == "" or row['ref_no'] is None
    assert "Tax for" in row['narration']

def test_dividend_fix():
    # User Case: "02/11/2025 1,504.00 81", "72012511010096CZ"
    lines = ["02/11/2025 1,504.00 81", "72012511010096CZ"]
    row = process_transaction_cluster(lines)
    assert row['ref_no'] == "72012511010096CZ"

def test_ips_charge_balance_noise():
    # 2025-11-13 5.00 ref="1,673,000.48" (balance)
    lines = ["13/11/2025 5.00 1,673,000.48", "IPS CHARGE"]
    row = process_transaction_cluster(lines)
    assert row['amount'] == 5.00
    assert row['ref_no'] == "" or row['ref_no'] is None
    # 1,673... should be filtered out? 
    # It might be in 'amounts' if regex matches valid amount, but skipped by logic valid_amounts? 
    # Or if regex matches amount, it's removed from 'other_tokens', so it won't be in narration.
    assert "1673000" not in row['narration'].replace(',','')

def test_pms_transfer():
    lines = ["28/08/2025 1,046,721.56", "478322208/12390", "BNKFT-PMS"]
    row = process_transaction_cluster(lines)
    assert row['ref_no'] == "478322208"
    assert "BNKFT-PMS" in row['narration']
    assert "/" not in row['ref_no']
