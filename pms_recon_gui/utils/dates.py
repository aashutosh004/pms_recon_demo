from dateutil import parser
from datetime import datetime, date
from typing import Optional

def parse_date(date_str: str) -> Optional[date]:
    """
    Parse a date string into a python date object.
    Supports DD/MM/YYYY format commonly used in Nepal banking.
    Returns None if parsing fails.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    try:
        # First try the specific format found in bank statements (DD/MM/YYYY)
        return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
    except ValueError:
        pass
    
    try:
        # Fallback to dateutil default parsing
        dt = parser.parse(date_str, dayfirst=True)
        return dt.date()
    except (ValueError, TypeError):
        return None

def format_date_iso(d: date) -> str:
    """Format date as YYYY-MM-DD string"""
    if d:
        return d.isoformat()
    return ""
