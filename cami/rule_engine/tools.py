import json

from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from cami.tools import BillLineItemField, list_bill_items_as_data


def correct_approvals(bill_items):
    print("Correcting Approvals")
    sum_insured = 500000
    for item in bill_items:
        print(f"Item: {item}")
        if item["is_eligible"]:
            approvable_amount = min(sum_insured, item["approved_amount"])
            item["approved_amount"] = approvable_amount
            sum_insured -= approvable_amount
        else:
            item["approved_amount"] = 0
        print(f"Item after correction: {item}")

    return bill_items


async def bill_report_tool(patient_id: str, tool_context: ToolContext) -> str:
    """Verify the bill items claim against the policy document.

    Returns:
        str: Markdown formatted bill items report for user review
    """
    from .agents import output_formatter_agent, rule_engine_agent

    # print("Claim: {}".format(claim))
    # bill_items = claim.get("bill_items", [])
    # tool_context.state["claim:bill_items"] = bill_items

    claim: list[BillLineItemField] = await list_bill_items_as_data(patient_id=patient_id)

    rule_engine_agent = AgentTool(agent=rule_engine_agent)
    result = await rule_engine_agent.run_async(
        args={"request": "claims from user"},  # Todo: What should we send?
        tool_context=tool_context,
    )
    bill_items = correct_approvals(json.loads(result.replace("\n", "").strip("```").strip("json")))
    tool_context.state["claim:rule_engine_output"] = bill_items

    review_agent_tool = AgentTool(agent=output_formatter_agent)
    result = await review_agent_tool.run_async(
        args={
            "request": "reviewing claims and approvals from the rule_engine_agent"
        },  # Todo: What should we send?
        tool_context=tool_context,
    )


#     Returns:
#         str: Markdown formatted bill items report for user review
#     """
#     bill_items = claim.get("bill_items", [])
#     tool_context.state["claim:bill_items"] = bill_items
#     agent_tool = AgentTool(agent=bill_eligibility_agent)
#     result = await agent_tool.run_async(
#         args={"request": "claims from user"},  # Todo: What should we send?
#         tool_context=tool_context,
#     )
#     cleaned_result = result.replace("\n", "").strip("```").strip("json")
#     cleaned_result = json.loads(cleaned_result)
#     print("Cleaned Result from AgentTool ", cleaned_result)

#     formatted_response = response_formatter(cleaned_result)
#     print("Formatted Response:", formatted_response)
#     return formatted_response
