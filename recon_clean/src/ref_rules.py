import re

def extract_ref(tokens: list, narration: str) -> str:
    """
    Extract best reference from tokens/narration.
    """
    low_narration = narration.lower()
    
    # 0. Safety: If it's a TAX row, avoid picking the account number
    if "tax for" in low_narration or "tax" in low_narration:
        # Check if we have a specific short UTR or something? 
        # User says: "Prefer ref_no=NULL".
        # So return empty unless we are very sure.
        return ""

    # 1. Look for CDS or Dividend (CZ) - High Priority
    for t in tokens:
        if t.startswith('CDS-'):
            return t
        if t.endswith('CZ') and len(t) > 10:
            return t
            
    # 2. Look for numeric ref with slash (Standard logic)
    for t in tokens:
        if '/' in t:
             parts = t.split('/')
             # Ensure left part is substantial digits
             if parts[0].isdigit() and len(parts[0]) > 6:
                 return parts[0]

    # 3. Look for long numeric (e.g. 478322208)
    # Exclude tokens that look like amounts (contain comma or dot)
    # Exclude tokens that are too short (like "12", "81")
    # Exclude tokens that are huge (balance like 1,673,000.48 which matches amount regex)
    
    candidates = []
    for t in tokens:
        # Cleanup
        raw = t.replace(',', '')
        
        # Must be digits
        if not raw.isdigit():
            continue
            
        # Ignore small numbers (Day numbers etc)
        if len(raw) < 5: 
            continue
            
        # Ignore massive numbers that might be Account Numbers (20 digits) ?? 
        # User said for Tax row "06411701339531000001" was picked.
        if len(raw) > 16:
            continue
            
        # Ignore amounts? 
        # Usually amounts have dots, but what if 1500?
        # We rely on position in parser usually, but here we just check tokens.
        # If the token was present in the "valid_amounts" list inside parser, we might want to skip it?
        # But we don't have that context here easily.
        
        candidates.append(t)
        
    if candidates:
        # Return the longest one? Or first?
        # Usually Ref is 9-12 digits.
        return candidates[0]
            
    return ""

def clean_narration(raw_narration: str) -> str:
    """
    Reduce narration to salient tokens.
    """
    # Remove dates, remove amounts? 
    # For now just normalize spaces.
    return re.sub(r'\s+', ' ', raw_narration).strip()
