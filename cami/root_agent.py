from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import (
    TRIAGE_INSTRUCTION,
)
from cami.tools import (
    check_membership,
    create_membership,
)
from cami.agents import claim_agent
from cami.policy import policy_agent, on_after_membership_tool, check_existing_policy


triage_agent = Agent(
    name="triage_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=TRIAGE_INSTRUCTION,
    description="Main customer service and triaging agent.",
    sub_agents=[policy_agent, claim_agent],
    tools=[check_membership, create_membership, check_existing_policy],
    after_tool_callback=on_after_membership_tool,
)
