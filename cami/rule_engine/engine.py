

class RuleEngine:
    def __init__(self, bill_items):
        self.bill_items = bill_items

    def process(self):
        # Todo: Implement deductible and co-pay

        print("-------- RuleEngine --------")
        print(f"Bill Items: {type(self.bill_items)} - ", self.bill_items)
        # Since we do not have history of claims, let us assume no claims
        # remaining_sum = self.claim.patient.policy.sum_insured
        remaining_sum = 500000  # Todo: Change this to get from patient details

        for bill_item in self.bill_items:
            claim_amount = bill_item["amount"]

            if claim_amount <= remaining_sum:
                approved_amount = claim_amount
                remaining_sum -= claim_amount
            else:
                approved_amount = remaining_sum
                remaining_sum = 0

            bill_item["approved_amount"] = approved_amount

        return self.bill_items
