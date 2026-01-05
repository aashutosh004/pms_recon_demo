import re

def extract_ref(tokens: list, narration: str) -> str:
    """
    Extract best reference from tokens/narration.
    Strategies:
    - If '/' in token -> strip suffix (e.g. 47832208/1230 -> 47832208)
    - If CDS-xxx -> CDS-xxx
    - If Dividend (CZ suffix) -> Keep it
    """
    # 1. Look for CDS
    for t in tokens:
        if t.startswith('CDS-'):
            return t
            
    # 2. Look for Dividend (CZ)
    for t in tokens:
        if t.endswith('CZ') and len(t) > 10:
            return t
            
    # 3. Look for numeric ref with slash
    for t in tokens:
        if '/' in t:
             parts = t.split('/')
             if parts[0].isdigit() and len(parts[0]) > 6:
                 return parts[0]
                 
    # 4. Look for long numeric
    for t in tokens:
        if t.isdigit() and len(t) > 6:
            return t
            
    return ""

def clean_narration(raw_narration: str) -> str:
    """
    Reduce narration to salient tokens.
    """
    # Remove dates, remove amounts? 
    # For now just normalize spaces.
    return re.sub(r'\s+', ' ', raw_narration).strip()
