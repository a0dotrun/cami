from dataclasses import dataclass
from .policy import DefaultPolicy


class PatientPolicy:
    def __init__(self):
        self.policy_taken = DefaultPolicy()
        self.start_date = None
        self.end_date = None
        self.sum_insured = 500000  # Give a default of 5L


@dataclass
class Patient:
    name: str
    age: int
    gender: str
    policy: PatientPolicy
