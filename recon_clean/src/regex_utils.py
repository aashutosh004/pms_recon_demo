import re

# Date pattern: DD/MM/YYYY or YYYY-MM-DD
DATE_PATTERN = re.compile(r'(\d{2}/\d{2}/\d{4})|(\d{4}-\d{2}-\d{2})')

# Amount pattern: 1,234.56, -123.45 (optionally inside text)
# We need to be careful with dots in dates vs amounts.
AMOUNT_PATTERN = re.compile(r'[\-\+]?\s*[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?')

# Ref candidate: Alphanumeric, maybe with /
REF_CANDIDATE = re.compile(r'[A-Za-z0-9/\-]+')
