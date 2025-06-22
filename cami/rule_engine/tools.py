import json

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .engine import RuleEngine


def response_formatter(bill_items):
    response = ""
    for item in bill_items:
        response += f"""
            **{item['name']}** 
            Claimed Amount: {item['claimed_amount']}
            Approved Amount: {item['approved_amount']}
            Reason: {item['reason']}
        """
    return response


async def bill_report_tool(claim: dict, tool_context: ToolContext) -> str:
    """
    Verify the bill items claim against the policy document

    Args:
        claim (dict): Claim document

    Returns:
        str: Markdown formatted bill items report for user review
    """
    from .agents import bill_eligibility_agent

    bill_items = claim.get('bill_items', [])
    tool_context.state["claim:bill_items"] = bill_items
    agent_tool = AgentTool(agent=bill_eligibility_agent)
    result = await agent_tool.run_async(
        args={"request": "claims from user"},  # Todo: What should we send?
        tool_context=tool_context
    )
    cleaned_result = result.replace("\n", "").strip("```").strip("json")
    cleaned_result = json.loads(cleaned_result)
    print('Cleaned Result from AgentTool ', cleaned_result)

    formatted_response = response_formatter(cleaned_result)
    print("Formatted Response:", formatted_response)
    return formatted_response
