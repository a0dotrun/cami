import datetime
from dataclasses import dataclass

from .patient import Patient
from .policy import DefaultPolicy


@dataclass
class BillItem:
    procedure: str
    amount: float


@dataclass
class Claim:
    patient: Patient
    hospital: str  # Todo: Ideally a Hospital class, that can represent within network or not.
    date: datetime.datetime
    policy: DefaultPolicy
    bill_items: list[BillItem]
