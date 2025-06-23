import os
from google.adk.agents.readonly_context import ReadonlyContext


def rule_engine_agent_instructions(context: ReadonlyContext) -> str:
    bill_items = context.state.get('claim:bill_items', [])
    print("Bill Items from the state: {}".format(bill_items))

    policy_doc_path = os.path.join(os.getcwd(), "cami/storage/policy-lite.md")
    print("Policy Path: {}".format(policy_doc_path))

    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the RuleEngine as the algorithm to determine the eligibility for each bill item.
        
        <RuleEngine>
            As a **RuleEngine**, your task is to validate individual **bill items** within a claim. Process each bill item according to these sequential steps, ensuring all limits are strictly adhered to:

            1.  **Eligibility Assessment**: For every bill item, first determine its **eligibility**.
            2.  **Mark Eligibility**: If a bill item is eligible, add a boolean field named `is_eligible` and set its value to `true`.
            3.  **Calculate Initial Approvable Amount**:
                * **For Rents (e.g., Room Rent, ICU Charges)**: If the bill item is categorized as "Rents," calculate the initial approvable amount based on the **per daily limit** for each day claimed.
                * **For All Other Items**: For all other bill items, the initial approvable amount is the `claimed_amount`.
            4.  **Apply Sum Insured Cap**:
                * Compare the `initial approvable amount` (calculated in step 3) with the currently available `sum_insured`.
                * The `approved_amount` for the current bill item must be the **minimum** of these two values: `initial approvable amount` and `sum_insured`.
            5.  **Handle Exhausted Sum Insured**: If, after processing previous items, the `sum_insured` has already been **exhausted** (i.e., it's 0 or less), then the `approved_amount` for the current bill item must be `0`. This check should implicitly cover step 4, ensuring no approval if no sum insured remains.
            6.  **Update Sum Insured**: After determining the `approved_amount` for the current bill item, **deduct this `approved_amount` from the `sum_insured`** for subsequent bill items. This ensures the `sum_insured` accurately reflects the remaining balance.
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
            
            **Output Format:**
            * The final response must be a **pure JSON array** of bill items. Each object in the array must contain only the following five fields: `name`, `claimed_amount`, `approved_amount`, `is_eligible`, and `reason`.
            * The entire response must start with `[` and end with `]`. No extra text or Markdown code block delimiters (` ```json`, ` ``` `) are allowed.
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


def formatter_agent_instructions(context: ReadonlyContext) -> str:
    rule_engine_output = context.state.get('claim:rule_engine_output', [])

    instruction = f"""
        You are a Markdown table formatter. Your task is to convert the provided array of items into a well-formatted Markdown table.
        The table must include a header row derived from the keys of the items, and each item should be a row in the table.
        Ensure all values are presented clearly.
        Your output should be *only* the Markdown table, with no additional text, explanations, or code block delimiters (e.g., ```).
        
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the Review as the algorithm to review the claims
        
        <Input>
            {rule_engine_output}
        </Input>
    """

    print("Markdown instruction of approvals: {}".format(instruction))
    return instruction

