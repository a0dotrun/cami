from .claim import Claim, BillItem
from .policy import DefaultPolicy
from .patient import Patient, PatientPolicy


class RuleEngine:
    def __init__(self, claim):
        self.claim = claim

    def process(self):
        # Todo: Implement deductible and co-pay

        # Since we do not have history of claims, let us assume no claims
        # remaining_sum = self.claim.patient.policy.sum_insured
        remaining_sum = 500000  # Todo: Change this to get from patient details

        for bill_item in self.claim["bill_items"]:
            claim_amount = bill_item["amount"]

            if claim_amount <= remaining_sum:
                approved_amount = claim_amount
                remaining_sum -= claim_amount
            else:
                approved_amount = remaining_sum
                remaining_sum = 0

            bill_item["approved_amount"] = approved_amount

        return self.claim.bill_items
