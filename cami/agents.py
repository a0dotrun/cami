from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import (
    claim_agent_instructions,
    discharge_agent_instructions,
)
from cami.rule_engine.tools import process_claim
from cami.tools import (
    add_bill_item,
    bill_report_status,
    check_ongoing_claim,
    discharge_report_form,
    discharge_report_status,
    list_bill_items,
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

