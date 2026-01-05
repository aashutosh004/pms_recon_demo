from datetime import date, timedelta
from typing import Optional
from rapidfuzz import fuzz

def within_date_window(d1: date, d2: date, window_days: int = 2) -> bool:
    """Check if d2 is within d1 ± window_days"""
    if not d1 or not d2:
        return False
    delta = abs((d1 - d2).days)
    return delta <= window_days

def compute_tolerance(bank_amount: float, narration: str, config: dict) -> float:
    """
    Compute applicable tolerance based on config and rules.
    Rules:
    - IPS charge in narration -> range [min, max]. We return max for safety check.
    - RTGS limit -> add flat tolerance.
    """
    tol_cfg = config.get('tolerance', {})
    base_tolerance = 0.0
    
    narration_u = str(narration).upper()
    amount_abs = abs(bank_amount)
    
    # IPS Rule
    if "IPS" in narration_u:
        # Use the max defined IPS tolerance
        base_tolerance = max(base_tolerance, float(tol_cfg.get('ips_max', 10.0)))
        
    # RTGS Rule
    rtgs_threshold = float(tol_cfg.get('rtgs_threshold', 2000000.0))
    if amount_abs >= rtgs_threshold:
        base_tolerance += float(tol_cfg.get('rtgs_flat', 100.0))
        
    return base_tolerance

def check_similarity(s1: str, s2: str, threshold: float = 0.85) -> bool:
    """
    Check fuzzy similarity between two strings.
    """
    if not s1 or not s2:
        return False
    
    # token_set_ratio is good for partial overlap like "BNKFT-PMS" vs "PMS charge"
    score = fuzz.token_set_ratio(str(s1), str(s2)) / 100.0
    return score >= threshold
