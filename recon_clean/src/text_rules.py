import re

def clean_particulars(text: str) -> str:
    """
    Clean Broker Particulars.
    - Normalize whitespace.
    - Fix "+ ," -> "+" etc.
    - Fix "H- O-" -> "H-O-"
    """
    if not isinstance(text, str):
        return ""
    
    s = text.strip()
    # Collapse multiple spaces
    s = re.sub(r'\s+', ' ', s)
    
    # Fix separated symbols
    s = s.replace('+ ,', '+')
    s = s.replace('- ,', '-')
    
    # Fix split hyphens "H- O-" -> "H-O-"
    s = re.sub(r'([A-Z])-\s+([A-Z])', r'\1-\2', s)
    
    return s.strip()

def is_noise_line(line: str) -> bool:
    """
    Check if a line is header/footer noise.
    """
    l = line.lower()
    if 'collect' in l: return True
    if 'date summary' in l: return True
    if 'dr count' in l and 'cr count' in l: return True
    if 'branch,' in l: return True
    if 'continued page' in l: return True
    return False
