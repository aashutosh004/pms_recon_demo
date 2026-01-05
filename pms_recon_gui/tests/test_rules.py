import pytest
from datetime import date
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.rules import within_date_window, compute_tolerance, check_similarity

def test_within_date_window():
    d1 = date(2025, 1, 10)
    d2 = date(2025, 1, 12)
    assert within_date_window(d1, d2, 2) is True
    assert within_date_window(d1, d2, 1) is False
    
    d3 = date(2025, 1, 8)
    assert within_date_window(d1, d3, 2) is True

def test_compute_tolerance():
    config = {
        'tolerance': {
            'ips_min': 2.0,
            'ips_max': 10.0,
            'rtgs_flat': 100.0,
            'rtgs_threshold': 2000000.0
        }
    }
    
    # Normal case
    assert compute_tolerance(1000, "PAYMENT", config) == 0.0
    
    # IPS case
    assert compute_tolerance(500, "IPS CHARGE", config) == 10.0
    
    # RTGS case
    assert compute_tolerance(2500000, "Fund Transfer", config) == 100.0
    
    # IPS + RTGS? 2.5M IPS
    # The code adds flat to base. base is max(0, 10). So 10 + 100 = 110.
    assert compute_tolerance(2500000, "IPS TRANSFER", config) == 110.0

def test_similarity():
    assert check_similarity("BNKFT Ref123", "Ref123", 0.85) is True
    assert check_similarity("Totally Different", "Nothing Alike", 0.85) is False
