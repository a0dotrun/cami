from google.adk.agents import Agent

from cami.agent.prompts import MAIN_AGENT_INSTRUCTIONS
from cami.config import MODEL_GEMINI_2_0_FLASH

agent = Agent(
    name="ClaimInsuranceAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=MAIN_AGENT_INSTRUCTIONS,
    tools=[],
)
