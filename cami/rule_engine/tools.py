from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from .db_utils import get_patient_info
from .formatter_agent import output_formatter_agent
from .rule_engine_agent import verify_claim_agent


async def correct_approvals(patient_id, bill_items):
    print("Correcting Approvals")

    patient_info = await get_patient_info(patient_id=patient_id)
    sum_insured = patient_info.get("sum_insured", 0)
    for item in bill_items:
        print(f"Item: {item}")
        if item["is_eligible"]:
            approvable_amount = min(sum_insured, item["approved_amount"], item["claimed_amount"])
            item["approved_amount"] = approvable_amount
            sum_insured -= approvable_amount
        else:
            item["approved_amount"] = 0
        print(f"Item after correction: {item}")

    return bill_items


async def process_claim(patient_id: str, tool_context: ToolContext) -> str:
    """Process the claim for the Patient.

    Args:
        patient_id (str): Patient ID

    Returns:
        str: Markdown formatted processed claim report.
    """
    verify_claim_agent_as_tool = AgentTool(agent=verify_claim_agent)
    verified_bill = await verify_claim_agent_as_tool.run_async(
        args={"request": "verify claim based on my policy and provided bill items"},
        tool_context=tool_context,
    )

    print("****************** VERIFIED CLAIM AGENT AS TOOL ********************")
    print(verified_bill)
    print("****************** VERIFIED CLAIM AGENT AS TOOL ********************")

    print("****************** VERIFIED CLAIM AGENT AS TOOL CORRECTED ********************")
    verified_bill_corrected = await correct_approvals(patient_id, verified_bill["bill_items"])
    print(verified_bill_corrected)
    print("****************** VERIFIED CLAIM AGENT AS TOOL CORRECTED ********************")

    request = f"""Format the input JSON to markdown table, avoid extra text and explainations
    JSON: {verified_bill_corrected}
    """
    output_formatter_agent_as_tool = AgentTool(agent=output_formatter_agent)
    bill_items_verified = await output_formatter_agent_as_tool.run_async(
        args={
            "request": request,
        },
        tool_context=tool_context,
    )

    print("************** BILLS ITEMS VERIFIED ******************")
    print(bill_items_verified)
    print("************** BILLS ITEMS VERIFIED ******************")

    return bill_items_verified
