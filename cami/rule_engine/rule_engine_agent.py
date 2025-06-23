from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from pydantic import BaseModel, Field

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.storage.policies import get_doc_from_policy
from cami.tools import BillLineItemField

from .db_utils import get_info


def format_bill_items(items: list[BillLineItemField]) -> str:
    output = []
    for item in items:
        output.append("<item>")
        output.append(f" - name: {item.name}")
        output.append(f" - charges: {item.charges}")
        output.append("</item>")
    return "\n".join(output)


async def get_instructions(context: ReadonlyContext) -> str:
    bill_items = context.state.get("claim:bill_items", [])
    bills = format_bill_items(bill_items)

    patient_id = context.state.get("user:patient_id")
    info = await get_info(patient_id)
    doc = get_doc_from_policy(policy_id=info["policy_id"])

    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        Use the RuleEngine as the algorithm to determine the eligibility for each bill item.

        <RuleEngine>
            As a **RuleEngine**, your task is to validate individual **bill items** within a claim. Process each bill item according to these sequential steps:

            1.  **Eligibility Assessment**: For every bill item, first determine its **eligibility**.
            2.  **Mark Eligibility**: If a bill item is eligible, add a boolean field named `is_eligible` and set its value to `true`.
            3.  **Skip Processing**: If the bill item is not eligible or the `remaining_sum_insured`, then update `approved_amount` to 0 and continue to next bill item. 
            3.  **Calculate Initial Approvable Amount**:
                * **For "Rents" (e.g., Room Rent, ICU Charges)**: If the bill item is categorized as "Rents" and includes the number of days, calculate the `initial_approvable_amount` based on the **per daily limit** (from policy terms) multiplied by the `Hospitalisation Days` (found under `ClaimInfo`).
                * **For All Other Items**: For all other bill items, the `initial_approvable_amount` is the `claimed_amount`.
            4.  **Apply Sum Insured Cap**:
                * Compare the `initial_approvable_amount` (calculated in step 3) with the currently available `sum_insured`.
                * The `approved_amount` for the current bill item must be the **minimum** of these three values: `claimed_amount`, `initial approvable amount` and `sum_insured`.
            5. **Apply Co-payment Rules**:
                * **Determine Applicable Co-payment Percentage**: Based on the `Policy Type` (e.g., "Cami Lite", "Cami Pro"), `Insured Member's Age`, and `Hospital Type` (e.g., "Network", "Non-Network") (all found under `ClaimInfo` or `PolicyInfo`), identify the total applicable co-payment percentage.
                * **Calculate Co-payment Amount**: Multiply the `approved_amount` (from step 4) by the `total applicable co-payment percentage`.
                * **Determine Final Payable Amount**: Subtract the `co-payment amount` from the `approved_amount`. This is the final `approved_amount` for the current bill item.
            6.  **Update Sum Insured**: After determining the `approved_amount` for the current bill item, **deduct this `approved_amount` from the `sum_insured`** for subsequent bill items. This ensures the `sum_insured` accurately reflects the remaining balance.
        </RuleEngine>
        
        <BillItems>
            {bills}
        </BillItems>

        **UserInfo**
        - *Name:* {info.get("user_name")}
        - *Age:* {info.get("age")}
        - *Sum Insured:* {info.get("sum_insured")}
    
        **ClaimInfo**
            - *Hospitalisation Days:* {info.get("hospitalisation_days")}
            - *Hospital Type:* {info.get("hospital_in_network")}
    
        <PolicyDocument>            
            {doc}
        </PolicyDocument>

        **Output Format:**
        * The final response must be a **pure JSON array** of bill items. Each object in the array must contain only the following five fields: `name`, `claimed_amount`, `approved_amount`, `is_eligible`, and `reason`.
        * The entire response must start with `[` and end with `]`. No extra text or Markdown code block delimiters (` ```json`, ` ``` `) are allowed.
    """

    print(f"Prepared Policy Doc: {instruction}")
    return instruction


# 1. Define your individual Output Pydantic model
class BillItemValidationOutput(BaseModel):
    """Represents the validation result for a single bill item."""

    name: str = Field(description="Name of the bill item, e.g., 'Dialysis', 'Room Rent'")
    claimed_amount: float = Field(description="The amount claimed for this bill item.")
    approved_amount: float = Field(
        description="The final approved amount for this bill item after all policy rules and sum insured limits."
    )
    is_eligible: bool = Field(
        description="True if the bill item is eligible according to policy rules, False otherwise."
    )
    reason: str = Field(
        description="A concise explanation for the approved amount, including why it was capped or denied."
    )


class BillItems(BaseModel):
    """Represents a list of BillItemValidationOutput."""

    bill_items: list[BillItemValidationOutput] = Field(
        description="List of BillItemValidationOutput."
    )


rule_engine_agent = Agent(
    name="rule_engine_agent",
    description="A helpful insurance agent, that verifies the claim for individual bill items and determine their eligibility.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=get_instructions,
    output_schema=BillItems,
    tools=[],
)
