from typing import Any

from google.adk.agents import Agent
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
from cami.rule_engine.tools import process_claim
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
        process_claim,
    ],
)

