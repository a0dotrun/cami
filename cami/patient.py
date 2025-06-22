from dataclasses import dataclass


class PatientPolicy:
    def __init__(self):
        self.policy_taken = ""  # Should be cami-lite or cami-pro

        # Todo: Can be filled-up and considered in the context of a claim
        self.start_date = None
        self.end_date = None

    @property
    def sum_insured(self):
        if self.policy_taken == "cami-lite":
            return 500000
        else:
            return 1500000


@dataclass
class Patient:
    name: str
    age: int
    gender: str
    policy: PatientPolicy
