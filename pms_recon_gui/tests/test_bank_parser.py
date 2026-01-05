import pytest
from datetime import date
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.bank_txt_parser import parse_bank_line, parse_bank_statement

def test_parse_bank_line_valid():
    line = "28/08/2025 478322208/12390 1,046,729.56 BNKFT-PMS PMS-CIPS"
    result = parse_bank_line(line)
    
    assert result is not None
    assert result['txn_date'] == date(2025, 8, 28)
    assert result['ref_no'] == "478322208"
    assert result['amount'] == 1046729.56
    assert result['narration'] == "BNKFT-PMS PMS-CIPS"

def test_parse_bank_line_invalid_date():
    line = "INV-DATE 478322208 100.00 Narration"
    result = parse_bank_line(line)
    assert result is None

def test_parse_bank_statement_full():
    content = """28/08/2025 Ref1 100.00 Narration One
    29/08/2025 Ref2 200.50 Narration Two
    """
    df = parse_bank_statement(content)
    assert len(df) == 2
    assert df.iloc[0]['ref_no'] == "Ref1"
    assert df.iloc[1]['amount'] == 200.50
