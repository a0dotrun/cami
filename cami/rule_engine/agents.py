from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from cami.config import MODEL_GEMINI_2_0_FLASH
from .prompts import procedure_claim_agent_instructions


procedure_claim_agent = Agent(
    name="claim_agent",
    description="A helpful insurance agent, that verifies the claim for individual bill items and determine their eligibility.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=procedure_claim_agent_instructions,
    tools=[]
)
