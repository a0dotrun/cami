from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool


async def bill_report_tool(claim: dict, tool_context: ToolContext) -> str:
    """
    Verify the bill items claim against the policy document

    Args:
        claim (dict): Claim document

    Returns:
        str: Markdown formatted bill items report for user review
    """
    from .agents import rule_engine_agent, review_agent

    bill_items = claim.get('bill_items', [])
    tool_context.state["claim:bill_items"] = bill_items
    rule_engine_agent = AgentTool(agent=rule_engine_agent)
    result = await rule_engine_agent.run_async(
        args={"request": "claims from user"},  # Todo: What should we send?
        tool_context=tool_context
    )
    tool_context.state["claim:rule_engine_output"] = result
    review_agent_tool = AgentTool(agent=review_agent)
    result = await review_agent_tool.run_async(
        args={"request": "reviewing claims and approvals from the rule_engine_agent"},  # Todo: What should we send?
        tool_context=tool_context
    )

    print('Result from AgentTool ', result)
    return result
