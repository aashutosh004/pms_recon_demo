import pytest
import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ref_rules import extract_ref, clean_narration
from bank_parser import process_transaction_cluster

def test_pms_transfer_ref():
    tokens = ["47832208/1230", "BANK-PMS"]
    ref = extract_ref(tokens, "")
    # Rules say extract best ref candidate.
    # Logic might return "47832208/1230". 
    # bank_parser.py handles the splitting of suffix.
    assert "47832208" in ref

def test_dividend_merge():
    lines = ["21/11/2025 1,594.00 0.00", "1,594.00 CD"]
    row = process_transaction_cluster(lines)
    
    assert row['txn_date'] == "2025-11-21"
    assert row['amount'] == 1594.00
    # Narration should be clean "CD" or similar
    assert "CD" in row['narration']

def test_ref_priority_dividend():
    # Dividend row w/ ref_no=720125110090CZ
    lines = ["02/11/2025 500.00 Dividend", "720125110090CZ"]
    row = process_transaction_cluster(lines)
    assert row['ref_no'] == "720125110090CZ"
    
def test_noise_removal():
    from text_rules import is_noise_line
    assert is_noise_line("Date Summary") is True
    assert is_noise_line("Collect 1/2") is True
