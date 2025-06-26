from typing import Any

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from cami.utils import logger
from .schema import MembershipResponse


def on_after_membership_tool(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> None | dict:

    logger.info(f"Inside on_after_membership_tool hook, toolResponse: {tool_response}")
    if not tool_response:
        return None

    def format_result(result: MembershipResponse) -> str:
        return f"""User ID: {result.user_id}\n
        First Name: {result.first_name}\n
        Last Name: {result.last_name}\n
        """

    tool_name = tool.name
    result_status = tool_response.get("status", "")
    if tool_name in ("check_membership", "create_membership") and result_status == "success":
        result: dict = tool_response.get("result", {})
        response = MembershipResponse(**result)
        # set the user_id in the tool context state
        tool_context.state["user:user_id"] = response.user_id
        return {
            "status": result_status,
            "result": format_result(response),
        }
    return None
