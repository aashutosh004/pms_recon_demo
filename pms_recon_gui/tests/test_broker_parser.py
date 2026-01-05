import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.broker_pdf_parser import normalize_pdf_table_headers, extract_ref_from_particulars

def test_normalize_headers():
    data = [
        ["Header1", "Header2", "Header3"],
        ["Date", "Particulars", "Debit"],
        ["2025-01-01", "Test", "100"]
    ]
    df = pd.DataFrame(data)
    
    norm_df = normalize_pdf_table_headers(df)
    
    assert "Particulars" in norm_df.columns
    assert len(norm_df) == 1
    assert norm_df.iloc[0]["Particulars"] == "Test"

def test_extract_ref():
    text = "Received in BANK ... Reference No.: 478322208"
    ref = extract_ref_from_particulars(text)
    assert ref == "478322208"
    
    text2 = "Some other text Ref No: 12345"
    ref2 = extract_ref_from_particulars(text2)
    assert ref2 == "12345"

    text3 = "No ref here"
    ref3 = extract_ref_from_particulars(text3)
    assert ref3 is None
