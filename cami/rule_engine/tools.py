import json

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .engine import RuleEngine
from .agents import bill_eligibility_agent


async def rule_engine_tool(claim: dict, tool_context: ToolContext) -> list:
    """
    Verify the claim against the policy document

    Args:
        claim (dict): Claim document

    Returns:
        list: Bill Items with name, approved_amount, eligible and reason
    """

    bill_items = claim.get('bill_items', [])
    tool_context.state["claim:bill_items"] = bill_items
    agent_tool = AgentTool(agent=bill_eligibility_agent)
    result = await agent_tool.run_async(
        args={"request": "claims from user"},  # Todo: What should we send?
        tool_context=tool_context
    )
    cleaned_result = result.replace("\n", "").strip("```").strip("json")
    cleaned_result = json.loads(cleaned_result)

    updated_bill_items = RuleEngine(bill_items=cleaned_result).process()
    return updated_bill_items
