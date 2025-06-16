from .claim import Claim


class RuleEngine:
    def __init__(self, claim: Claim):
        self.claim = claim

    def process(self):
        policy = self.claim.policy
        bill_items = self.claim.bill_items

        # Since we do not have history of claims, let us assume no claims
        remaining_sum = self.claim.patient.policy.sum_insured
        results = []

        for bill_item in bill_items:
            procedure = bill_item.procedure
            claim_amount = bill_item.amount
            approved_amount = policy.process_procedure_claim(procedure) * claim_amount

            if claim_amount <= remaining_sum:
                remaining_sum -= claim_amount
            else:
                approved_amount = remaining_sum
                remaining_sum = 0

            results.append({
                "procedure": procedure,
                "amount": approved_amount,
            })

        return results
