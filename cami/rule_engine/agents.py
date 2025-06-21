from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from cami.config import MODEL_GEMINI_2_0_FLASH
from .prompts import bill_eligibility_agent_instructions


bill_eligibility_agent = Agent(
    name="claim_agent",
    description="A helpful insurance agent, that verifies the claim for individual bill items and determine their eligibility.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=bill_eligibility_agent_instructions,
    tools=[]
)
