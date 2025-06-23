from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from pydantic import BaseModel, Field

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.storage.policies import get_doc_from_policy
from cami.tools import BillLineItemField, list_bill_items_as_data

from .db_utils import get_patient_info


def format_bill_items(items: list[BillLineItemField]) -> str:
    output = []
    for item in items:
        output.append("<item>")
        output.append(f" - name: {item.name}")
        output.append(f" - charges: {item.charges}")
        output.append("</item>")
    return "\n".join(output)


async def claim_verification_instructions(context: ReadonlyContext) -> str:
    patient_id = context.state.get("user:patient_id")

    bills_formatted = "No Bill Items Found"
    response = await list_bill_items_as_data(patient_id=patient_id)
    if response.get("status") != "error":
        bills_formatted = format_bill_items(response["result"])

    patient_info = await get_patient_info(patient_id)
    policy_document = get_doc_from_policy(policy_id=patient_info["policy_id"])

    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the RuleEngine as the algorithm to determine the eligibility for each bill item.

        <RuleEngine>
            As a **RuleEngine**, your task is to validate individual **bill items** within a claim. Process each bill item according to these sequential steps:

            1.  **Eligibility Assessment**: For every bill item, first determine its **eligibility**.
            2.  **Mark Eligibility**: If a bill item is eligible, add a boolean field named `is_eligible` and set its value to `true`.
            3.  **Skip Processing**: If the bill item is not eligible or the `remaining_sum_insured` is 0, then update `approved_amount` to 0 and continue to next bill item. 
            4.  **Calculate Initial Approvable Amount**:
                * **For "Rents" (e.g., Room Rent, ICU Charges)**: If the bill item is categorized as "Rents" and includes the number of days, calculate the `initial_approvable_amount` based on the **per daily limit** (from policy terms) multiplied by the `Hospitalisation Days` (found under `ClaimInfo`).
                * **For All Other Items**: For all other bill items, the `initial_approvable_amount` is the `claimed_amount`.
            5.  **Apply Sum Insured Cap**:
                * Compare the `initial_approvable_amount` (calculated in step 4) with the currently available `sum_insured`.
                * The `approved_amount` for the current bill item must be the **minimum** of these three values: `claimed_amount`, `initial approvable amount` and `sum_insured`.
            6. **Apply Co-payment Rules**:
                * **Determine Applicable Co-payment Percentage**: Based on the `Policy Type` (e.g., "Cami Lite", "Cami Pro"), `Insured Member's Age`, and `Hospital Type` (e.g., "Network", "Non-Network") (all found under `ClaimInfo` or `PolicyInfo`), identify the total applicable co-payment percentage.
                * **Calculate Co-payment Amount**: Multiply the `approved_amount` (from step 5) by the `total applicable co-payment percentage`.
                * **Determine Final Payable Amount**: Subtract the `co-payment amount` from the `approved_amount`. This is the final `approved_amount` for the current bill item.
            7.  **Update Sum Insured**: After determining the `approved_amount` for the current bill item, **deduct this `approved_amount` from the `sum_insured`** for subsequent bill items. This ensures the `sum_insured` accurately reflects the remaining balance.
        </RuleEngine>

        <BillItems>
            {bills_formatted}
        </BillItems>

        <UserInfo>
        - *Name:* {patient_info.get("user_name")}
        - *Age:* {patient_info.get("age")}
        - *Sum Insured:* {patient_info.get("sum_insured")}
        </UserInfo>

        <ClaimInfo>
            - *Hospitalisation Days:* {patient_info.get("hospitalisation_days")}
            - *Hospital Type:* {patient_info.get("hospital_in_network")}
        </ClaimInfo>

        <PolicyDocument>
            {policy_document}
        </PolicyDocument>

        **Output Format:**
        * The final response must be a **pure JSON array** of bill items. Each object in the array must contain only the following five fields: `name`, `claimed_amount`, `approved_amount`, `is_eligible`, and `reason`.
        * The entire response must start with `[` and end with `]`. No extra text or Markdown code block delimiters (` ```json`, ` ``` `) are allowed.
    """

    print(f"Prepared Policy Doc: {instruction}")
    return instruction


class BillItemValidationOutput(BaseModel):
    name: str = Field(description="Name of the bill item, e.g., 'Dialysis', 'Room Rent'")
    claimed_amount: float = Field(description="The amount claimed for this bill item.")
    approved_amount: float = Field(description="The final approved amount for this bill item after all policy rules and sum insured limits."
    )
    is_eligible: bool = Field(
        description="True if the bill item is eligible according to policy rules, False otherwise."
    )
    reason: str = Field(
        description="A concise explanation for the approved amount, including why it was capped or denied."
    )


class VerifiedBill(BaseModel):
    bill_items: list[BillItemValidationOutput] = Field(description="List of verified bill items")


verify_claim_agent = Agent(
    name="verify_claim_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=claim_verification_instructions,
    output_schema=VerifiedBill,
)
