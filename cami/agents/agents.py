"""Module provides agents definitions"""

from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_PRO
from cami.prompts import (
    DISCHARGE_SUMMARY_AGENT,
    MEMBERSHIP_INSTRUCTION,
    ROOT_INSTRUCTION,
)
from cami.tools.tools import (
    create_membership,
    get_discharge_summary_report,
    get_membership,
    get_summary_template,
    update_summary_field,
)

discharge_summary_agent = Agent(
    name="discharge_summary_agent",
    model=MODEL_GEMINI_2_0_PRO,
    instruction=DISCHARGE_SUMMARY_AGENT,
    tools=[get_summary_template, update_summary_field],
)


membership_agent = Agent(
    name="membership_agent",
    model=MODEL_GEMINI_2_0_PRO,
    description="Registers new patients",
    instruction=MEMBERSHIP_INSTRUCTION,
    tools=[get_membership, create_membership],
)

root_agent = Agent(
    name="root_agent",
    model=MODEL_GEMINI_2_0_PRO,
    instruction=ROOT_INSTRUCTION,
    sub_agents=[membership_agent, discharge_summary_agent],
    tools=[get_discharge_summary_report],
)
