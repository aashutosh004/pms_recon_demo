import pytest
import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from text_rules import clean_particulars

def test_clean_particulars_whitespace():
    raw = "Being Share Purchased   GBIME-1000.0@252.00 "
    expected = "Being Share Purchased GBIME-1000.0@252.00"
    assert clean_particulars(raw) == expected

def test_clean_particulars_hyphens():
    raw = "Bill No. H- O- P8283"
    expected = "Bill No. H-O-P8283"
    # Actually logic only handles "A- B", let's check regex in text_rules.py
    # Regex: r'([A-Z])-\s+([A-Z])' -> r'\1-\2'
    # "H- O" -> "H-O"
    assert clean_particulars(raw) == expected

def test_clean_particulars_symbols():
    raw = "Received in BANK + , Reference"
    expected = "Received in BANK + Reference"
    assert clean_particulars(raw) == expected
