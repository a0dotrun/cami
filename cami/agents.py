from typing import Any

from google.adk.agents import Agent

from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import (
    TRIAGE_INSTRUCTION,
    claim_agent_instructions,
    discharge_agent_instructions,
    policy_agent_instructions,
)

from cami.rule_engine.tools import verify_claim_tool
from cami.tools import (
    add_bill_item,
    available_policies,
    bill_report_status,
    check_existing_policy,
    check_membership,
    check_ongoing_claim,
    create_membership,
    discharge_report_form,
    discharge_report_status,
    list_bill_items,
    policy_faqs,
    purchase_policy,
    start_claim,
    update_bill_report_item,
    update_bill_report_status,
    update_discharge_report_form_field,
    update_discharge_report_status,
)

discharge_agent = Agent(
    name="discharge_agent",
    description="A helpful agent that can help customer with discharge report, filling and updating.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=discharge_agent_instructions,
    tools=[
        discharge_report_status,
        discharge_report_form,
        update_discharge_report_form_field,
        update_discharge_report_status,
    ],
)


bill_agent = Agent(
    name="bill_agent",
    description="A helpful agent that can help customer with bill report, status, filling, updating.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction="",
    tools=[
        bill_report_status,
        update_bill_report_status,
        add_bill_item,
        list_bill_items,
        update_bill_report_item,
    ],
)

claim_agent = Agent(
    name="claim_agent",
    description="A helpful agent that can help customer with insurance claims, ongoing claims and start claim process.",
    model=MODEL_GEMINI_2_0_FLASH,
    sub_agents=[discharge_agent, bill_agent],
    instruction=claim_agent_instructions,
    tools=[
        check_ongoing_claim,
        start_claim,
        verify_claim_tool
    ],
)


policy_agent = Agent(
    name="policy_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=policy_agent_instructions,
    description="A helpful agent that can help with insurance policy, purchase, listing and policy faqs.",
    tools=[
        available_policies,
        purchase_policy,
        check_existing_policy,
        policy_faqs,
    ],
)


class MembershipResponse(BaseModel):
    patient_id: str
    first_name: str
    last_name: str


def on_after_membership_tool(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> None | dict:
    if not tool_response:
        return None

    def format_result(result: MembershipResponse) -> str:
        return f"""Patient ID: {result.patient_id}\n
        First Name: {result.first_name}\n
        Last Name: {result.last_name}\n
        """

    tool_name = tool.name
    result_status = tool_response.get("status", "")
    if tool_name in ("check_membership", "create_membership") and result_status == "success":
        result: dict = tool_response.get("result", {})
        response = MembershipResponse(**result)
        # set the patient_id in the tool context state
        tool_context.state["user:patient_id"] = response.patient_id
        return {
            "status": result_status,
            "result": format_result(response),
        }
    return None


triage_agent = Agent(
    name="triage_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=TRIAGE_INSTRUCTION,
    description="Main customer service and triaging agent.",
    sub_agents=[policy_agent, claim_agent],
    tools=[check_membership, create_membership, check_existing_policy],
    after_tool_callback=on_after_membership_tool,
)
