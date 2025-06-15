from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts.base import (
    DISCHARGE_SUMMARY_AGENT,
    MEMBERSHIP_INSTRUCTION,
    ROOT_INSTRUCTION,
)
from cami.tools.base import (
    create_membership,
    get_discharge_summary_report,
    get_membership,
    get_discharge_summary_report,
    update_discharge_summary_field,
    discharge_summary_status,
)

discharge_summary_agent = Agent(
    name="discharge_summary_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=DISCHARGE_SUMMARY_AGENT,
    tools=[get_discharge_summary_report, update_discharge_summary_field],
)


membership_agent = Agent(
    name="membership_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Registers new patients",
    instruction=MEMBERSHIP_INSTRUCTION,
    tools=[get_membership, create_membership],
)

root_agent = Agent(
    name="root_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=ROOT_INSTRUCTION,
    sub_agents=[membership_agent, discharge_summary_agent],
    tools=[get_membership, create_membership, discharge_summary_status],
)
