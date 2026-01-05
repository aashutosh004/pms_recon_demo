from enum import Enum
from dataclasses import dataclass

class ExceptionCode(str, Enum):
    AMOUNT_MISMATCH = "E-001"
    DATE_MISMATCH = "E-002"
    REF_MISMATCH = "E-003"
    AMBIGUOUS_MATCH = "E-004"
    MISSING_COUNTER = "E-005"
    TOLERANCE_VIOLATION = "E-006"
    DATA_INTEGRITY = "E-007"
    CONFIG_ERROR = "E-008"

@dataclass
class ReconException:
    code: ExceptionCode
    description: str
    bank_ref: str = None
    broker_ref: str = None
