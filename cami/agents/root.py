from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.prompts import ROOT_INSTRUCTION

agent = Agent(
    name="ClaimInsuranceAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=ROOT_INSTRUCTION,
    tools=[],
)
