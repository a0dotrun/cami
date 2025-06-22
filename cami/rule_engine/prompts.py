import os
from google.adk.agents.readonly_context import ReadonlyContext


class SafeDict(dict):
    def __missing__(self, key):
        return f'{{{key}}}'  # Keeps the placeholder unchanged


def bill_eligibility_agent_instructions(context: ReadonlyContext) -> str:
    bill_items = context.state.get('claim:bill_items', [])
    print("Bill Items from the state: {}".format(bill_items))

    policy_doc_path = os.path.join(os.getcwd(), "cami/storage/policy-lite.md")
    print("Policy Path: {}".format(policy_doc_path))

    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the RuleEngine as the algorithm to determine the eligibility for each bill item.
        
        <RuleEngine>
            As a **RuleEngine**, your task is to validate individual **bill items** within a claim. Process each bill item according to these sequential steps:
            
            1.  **Eligibility Assessment**: For every bill item, first determine its **eligibility**.
            2.  **Mark Eligibility**: If a bill item is eligible, add a boolean field named `is_eligible` and set its value to `true`.
            3.  **Calculate Approved Amount**: Compute the `approved_amount` for the eligible bill item by deducting it from the available `sum_insured`.
            4.  **Sum Insured Exhaustion**: If the `sum_insured` has already been **exhausted** (i.e., it's 0 or less), then the `approved_amount` for the current bill item must be `0`.
            5.  **Partial Approval**: If the `sum_insured` is less than the calculated approvable amount for the current bill item, then the `approved_amount` should be set **equal to the remaining `sum_insured`**.
            6.  **Rent Processing**: Specifically for bill items categorized as **Rents**, if the claim is eligible, approve the amount based on the **per daily limit** for each day claimed.
        </RuleEngine>
        
        <BillItems>
            {bill_items}
        </BillItems>
    """
    with open(policy_doc_path) as f:
        doc = f.read()
        instruction += f"""
            <PolicyDocument>
                {doc}
            </PolicyDocument>
            -----
            
            Generate a **JSON array** of bill items. Each object in the array must contain only the following five fields:
            - `name`
            - `claimed_amount`
            - `approved_amount`
            - `is_eligible`
            - `reason`
            
            Your entire response must be **pure JSON**, starting with `[` and ending with `]`. Do not include any additional text, explanations, or Markdown code block delimiters (e.g., ` ```json` or ` ``` `).
        """

    total_claim_amount = 0
    for item in bill_items:
        total_claim_amount += item.get('amount', 0)
        print("Total claim amount: {}".format(total_claim_amount))

    instruction = (instruction
                   .replace("{total_claim_amount}", str(total_claim_amount))
                   .replace("{hospitalisation_days}", str(3)))

    print("Prepared Policy Doc: {}".format(instruction))
    return instruction
