from typing import Any

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import (
    DISCHARGE_INSTRUCTION,
    TRIAGE_INSTRUCTION,
)
from cami.tools import (
    available_policies,
    check_existing_policy,
    check_membership,
    create_membership,
    policy_faqs,
    purchase_policy,
)

discharge_agent = Agent(
    name="discharge_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=DISCHARGE_INSTRUCTION,
    tools=[],
)


def policy_agent_instructions(context: ReadonlyContext) -> str:
    patient_id = context.state.get("user:patient_id", "")
    return f"""You are a Insurance Policy Agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    Your customer Patient ID is: {patient_id}.
    Use the following routine to support the patient.
    1. Make sure Patient ID is available. Otherwise notify the user and collect the Patient ID.
    2. Check for existing policy for the Patient, Notify the patient of existing policy details.
    3. If there is no existing policy, ask the patient if they want to purchase a new policy. Display list of available policies.
    4. If the customer wants ask questions related to a policy, use policy faq tool to answer the questions.

    If the customer asks anything else, transfer back to the triage agent.
    """


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
    sub_agents=[policy_agent],
    tools=[check_membership, create_membership],
    after_tool_callback=on_after_membership_tool,
)
