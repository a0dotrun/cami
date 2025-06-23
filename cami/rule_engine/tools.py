from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from cami.tools import list_bill_items_as_data
from .formatter_agent import output_formatter_agent
from .rule_engine_agent import rule_engine_agent


def correct_approvals(bill_items):
    print("Correcting Approvals")
    sum_insured = 500000
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


async def verify_claim_tool(patient_id: str, tool_context: ToolContext) -> str:
    """Verify the bill items claim against the policy document.

    Args:
        patient_id (str): Patient ID

    Returns:
        str: Markdown formatted bill items report for user review
    """
    response = await list_bill_items_as_data(patient_id=patient_id)
    print("Response from list_bill_items_as_data ", response)
    if response.get("status") != "success":
        return "Error fetching bill items report"

    bill_items = response["result"]
    tool_context.state["claim:bill_items"] = bill_items
    rule_engine_agent_tool = AgentTool(agent=rule_engine_agent)
    result = await rule_engine_agent_tool.run_async(
        args={"request": "claims from user"},
        tool_context=tool_context,
    )
    print("Result from rule_engine_agent_tool ", result)
    bill_items = result["bill_items"]

    bill_items = correct_approvals(bill_items)
    tool_context.state["claim:rule_engine_output"] = bill_items
    output_formatter_agent_tool = AgentTool(agent=output_formatter_agent)
    result = await output_formatter_agent_tool.run_async(
        args={"request": "reviewing claims and approvals from the rule_engine_agent"},
        tool_context=tool_context,
    )
    return result
