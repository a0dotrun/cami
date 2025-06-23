import json

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool


def correct_approvals(bill_items):
    print("Correcting Approvals")
    sum_insured = 500000
    for item in bill_items:
        print("Item: {}".format(item))
        if item["is_eligible"]:
            approvable_amount = min(sum_insured, item["approved_amount"])
            item["approved_amount"] = approvable_amount
            sum_insured -= approvable_amount
        else:
            item["approved_amount"] = 0
        print("Item after correction: {}".format(item))

    return bill_items


async def bill_report_tool(claim: dict, tool_context: ToolContext) -> str:
    """
    Verify the bill items claim against the policy document

    Args:
        claim (dict): Claim document

    Returns:
        str: Markdown formatted bill items report for user review
    """
    from .agents import rule_engine_agent, output_formatter_agent

    print("Claim: {}".format(claim))
    bill_items = claim.get('bill_items', [])
    tool_context.state["claim:bill_items"] = bill_items
    rule_engine_agent = AgentTool(agent=rule_engine_agent)
    result = await rule_engine_agent.run_async(
        args={"request": "claims from user"},  # Todo: What should we send?
        tool_context=tool_context
    )
    bill_items = correct_approvals(json.loads(result.replace("\n", "").strip("```").strip("json")))
    tool_context.state["claim:rule_engine_output"] = bill_items

    review_agent_tool = AgentTool(agent=output_formatter_agent)
    result = await review_agent_tool.run_async(
        args={"request": "reviewing claims and approvals from the rule_engine_agent"},  # Todo: What should we send?
        tool_context=tool_context
    )

    print('Result from AgentTool ', result)
    return result
