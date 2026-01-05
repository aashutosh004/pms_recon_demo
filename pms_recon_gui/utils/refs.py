import re
from typing import Optional

def clean_ref_no(ref_raw: str) -> Optional[str]:
    """
    Clean reference number.
    - Strips suffixes after '/' (e.g., '478322208/12390' -> '478322208')
    - Removes whitespace
    """
    if not ref_raw:
        return None
    
    ref_raw = str(ref_raw).strip()
    
    # Split by '/' and take the first part
    if '/' in ref_raw:
        ref_raw = ref_raw.split('/')[0]
    
    # Remove any non-alphanumeric chars if needed (keeping basic for now)
    # But usually just stripping spaces is enough
    return ref_raw.strip() or None

def extract_tokens(text: str) -> list[str]:
    """Extract word tokens from text"""
    if not text:
        return []
    return re.findall(r'\w+', text)
