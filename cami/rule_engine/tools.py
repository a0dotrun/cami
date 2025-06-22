from typing import Any

from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel

from .engine import RuleEngine
from .agents import bill_eligibility_agent


async def rule_engine_tool(claim: dict, tool_context: ToolContext) -> dict:
    """
    Verify the claim against the policy document

    Args:
        claim (dict): Claim document

    Returns:
        dict: Claim document -- bill_items with approved_amount, eligibility and reason
    """

    tool_context.state["claim:bill_items"] = claim["bill_items"]
    agent_tool = AgentTool(agent=bill_eligibility_agent)
    result = await agent_tool.run_async(
        args={},  # Todo: What should we send?
        tool_context=tool_context
    )

    return RuleEngine(result).process()
