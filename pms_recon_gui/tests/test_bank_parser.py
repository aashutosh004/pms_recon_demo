import pytest
from datetime import date
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.bank_txt_parser import parse_bank_statement

def test_parse_simple_block():
    content = """
    2    28/08/2025    478322208/12390    1,046,729.56
         BNKFT-PMS
         PMS-CIPS
    """
    df = parse_bank_statement(content)
    assert len(df) == 1
    row = df.iloc[0]
    assert row['txn_date'] == date(2025, 8, 28)
    assert row['ref_no'] == "478322208"
    assert row['amount'] == 1046729.56
    assert "BNKFT-PMS" in row['narration']

def test_parse_complex_block_share_apply():
    content = """
    3    08/09/2025    Share apply: JHEL : 10    5.00
         0576
         CDS-215769794
         ~Date
    """
    df = parse_bank_statement(content)
    assert len(df) == 1
    row = df.iloc[0]
    assert row['txn_date'] == date(2025, 9, 8)
    # It should pick up CDS-... as ref
    assert "215769794" in row['ref_no'] or "CDS-215769794" in row['ref_no']
    assert row['amount'] == 5.00

def test_multiple_blocks():
    content = """
    2    28/08/2025    Ref1/123    100.00
    3    29/08/2025    Ref2        200.00
         Narration2
    """
    df = parse_bank_statement(content)
    assert len(df) == 2
    assert df.iloc[0]['amount'] == 100.00
    assert df.iloc[1]['amount'] == 200.00
    assert "Narration2" in df.iloc[1]['narration']
