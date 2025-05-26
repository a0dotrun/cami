from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.tools import claim_status

agent = Agent(
    name="ClaimInsuranceAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Helps users with their insurance claims.",
    instruction=(
        "You are Cami, an insurance claim assistant. "
        "When someone asks about their claim, use the 'claim_status' tool. "
        "If the tool fails, let them know politely. "
        "If it works, explain their claim status clearly and simply."
    ),
    tools=[claim_status],
)
