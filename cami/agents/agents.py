from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts.base import (
    DISCHARGE_INSTRUCTION,
    MEMBERSHIP_INSTRUCTION,
    ROOT_INSTRUCTION,
)
from cami.tools.base import (
    check_membership,
    create_membership,
    discharge_report,
    discharge_summary_status,
    update_discharge_summary_field,
    update_discharge_summary_status,
)

discharge_agent = Agent(
    name="discharge_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=DISCHARGE_INSTRUCTION,
    tools=[
        discharge_report,
        update_discharge_summary_field,
        update_discharge_summary_status,
    ],
)


membership_agent = Agent(
    name="membership_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Registers new patients",
    instruction=MEMBERSHIP_INSTRUCTION,
    tools=[check_membership, create_membership],
)

root_agent = Agent(
    name="customer_service_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=ROOT_INSTRUCTION,
    description="Main customer service agent and coordinator",
    sub_agents=[membership_agent, discharge_agent],
    tools=[check_membership, create_membership, discharge_summary_status],
)
