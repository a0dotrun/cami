from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import (
    TRIAGE_INSTRUCTION,
)
from cami.tools import (
    check_existing_policy,
    check_membership,
    create_membership,
)


triage_agent = Agent(
    name="triage_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=TRIAGE_INSTRUCTION,
    description="Main customer service and triaging agent.",
    sub_agents=[policy_agent, claim_agent],
    tools=[check_membership, create_membership, check_existing_policy],
    after_tool_callback=on_after_membership_tool,
)
