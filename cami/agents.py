from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import MAIN_AGENT_INSTRUCTIONS

agent = Agent(
    name="ClaimInsuranceAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=MAIN_AGENT_INSTRUCTIONS,
    tools=[],
)
