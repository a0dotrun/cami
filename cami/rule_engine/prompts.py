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
            
            Generate a **Markdown** response of bill items. Containing the following information
            - `name`
            - `claimed_amount`
            - `approved_amount`
            - `reason`
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


def review_agent_instructions(context: ReadonlyContext) -> str:
    rule_engine_output = context.state.get('claim:rule_engine_output', [])

    policy_doc_path = os.path.join(os.getcwd(), "cami/storage/policy-lite.md")
    print("Policy Path: {}".format(policy_doc_path))

    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the Review as the algorithm to review the claims
        
        **Policy Context and Rules for Review:**
        -   Track `remaining_sum_insured` sequentially. This is the absolute cap for any approval.
        -   **Sub-limits (apply BEFORE SI cap for each item):**
            -   ICU Charges: Daily limit ₹5,000 (e.g., 5 days * ₹5,000/day = ₹25,000).
            -   Room Rent: Daily limit ₹3,000 (e.g., 5 days * ₹3,000/day = ₹15,000).
            -   Ambulance Service: Capped at ₹2,000 per hospitalization.
            -   Nursing Charges: Daily limit ₹500/day.
            -   Consultation Charges (Pre/Post-hospitalization): Limit of ₹1,000 per visit.
            -   Post-hospitalization expenses: Limit of ₹7,000 (this is a total limit, not per-visit).

        <Review>
            ** Process each item sequentially **
            1.  **Parse Table**: Extract `Name`, `Claimed Amount`, `Approved Amount`, and `Reason` for each row.
            2.  **Calculate Expected Approved Amount**:
                * For the current item, first determine `amount_after_sub_limits`. If `Name` implies a daily or fixed sub-limit (e.g., "ICU Charges", "Room Rent", "Ambulance", "Nursing Charges", "Consultation"), apply that sub-limit. Otherwise, it's the `Claimed Amount`.
                * Then, compare `amount_after_sub_limits` with the `current_remaining_sum_insured`. The `expected_approved_amount` should be `min(amount_after_sub_limits, current_remaining_sum_insured)`.
            3.  **Compare and Flag Discrepancy**: Compare the `Approved Amount` from the table with your `expected_approved_amount`. If they differ significantly (e.g., more than a small rounding error), flag a discrepancy.
            4.  **Sum Insured Depletion**: After calculating the `expected_approved_amount`, deduct it from `current_remaining_sum_insured` for the next item. If `current_remaining_sum_insured` becomes 0 or less, ensure all *subsequent* items in the table have an `Approved Amount` of `0`.
            5.  **Reason Consistency**: Check if the `Reason` provided in the table is consistent with the `Approved Amount` (e.g., "Sum Insured exhausted" if approved amount is 0 due to SI).
            6.  **No Over-Claimed**: Ensure `Approved Amount` is never greater than `Claimed Amount`.
            
            Upon completing the initial processing, calculate the total Approved Amount across all items; if this sum exceeds the original_sum_insured, you must iteratively re-process the claim to ensure the total Approved Amount is capped by the original_sum_insured. 
        </Review>

        <ClaimBreakdownToReview>
            {rule_engine_output}
        </ClaimBreakdownToReview>
    """
    with open(policy_doc_path) as f:
        doc = f.read()
        instruction += f"""
            <PolicyDocument>
                {doc}
            </PolicyDocument>
            -----

            **Output Format:**
            Generate a **Markdown** response of bill items. Each row should contain only the following info and nothing else
            - `name`
            - `claimed_amount`
            - `approved_amount`
            - `reason`
        """

    instruction = instruction.replace("{hospitalisation_days}", str(3))

    print("Prepared Policy Doc: {}".format(instruction))
    return instruction

