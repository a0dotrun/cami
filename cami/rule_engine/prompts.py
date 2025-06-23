from pathlib import Path

from google.adk.agents.readonly_context import ReadonlyContext

from cami.tools import BillLineItemField, list_bill_items_as_data


class SafeDict(dict):
    def __missing__(self, key):
        """Return a placeholder for missing keys."""
        return f"{{{key}}}"  # Keeps the placeholder unchanged


def format_bill_items(items: list[BillLineItemField]) -> str:
    output = []
    for item in items:
        output.append("<item>")
        output.append(f" - name: {item.name}")
        output.append(f" - charges: {item.charges}")
        output.append("</item>")
    return "\n".join(output)


async def prcess_claim_instructions(context: ReadonlyContext) -> str:
    patient_id = context.state.get("user:patient_id", "")

    bills = ""

    response = await list_bill_items_as_data(patient_id=patient_id)
    if response.get("status") == "success":
        bills = format_bill_items(response["result"])
    else:
        bills = "Error fetching bills"

    print("****************** BILLS FROM DB *****************")
    print(f":{bills}")
    print("****************** BILLS FROM DB *****************")

    policy_doc_path = Path.cwd() / "cami/storage/policy-lite.md"
    print(f"Policy Path: {policy_doc_path}")

    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the RuleEngine as the algorithm to determine the eligibility for each bill item.

        <RuleEngine>
            As a **RuleEngine**, your task is to validate individual **bill items** within a claim. Process each bill item according to these sequential steps:

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
            {bills}
        </BillItems>
    """
    with policy_doc_path.open() as f:
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
            - `reason`

            Your entire response must be **pure JSON**, starting with `[` and ending with `]`. Do not include any additional text, explanations, or Markdown code block delimiters (e.g., ` ```json` or ` ``` `).
        """

    # total_claim_amount = 0
    # for item in response:
    #     total_claim_amount += item.get("amount", 0)
    #     print(f"Total claim amount: {total_claim_amount}")

    # instruction = instruction.replace("{total_claim_amount}", str(total_claim_amount)).replace(
    #     "{hospitalisation_days}", str(3)
    # )

    print("****************** INSTRUCTIONS *****************")
    print(f"Prepared Instructions: {instruction}")
    print("****************** INSTRUCTIONS *****************")
    return instruction
