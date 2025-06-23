from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from pydantic import BaseModel

from cami.config import MODEL_GEMINI_2_0_FLASH, MODEL_GEMINI_2_0_PRO
from .prompts import rule_engine_agent_instructions, formatter_agent_instructions
from . import bill_report_tool


rule_engine_agent = Agent(
    name="rule_engine_agent",
    description="A helpful insurance agent, that verifies the claim for individual bill items and determine their eligibility.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=rule_engine_agent_instructions,
    tools=[]
)

output_formatter_agent = Agent(
    name="review_agent",
    description="A helpful insurance agent, that reviews the processed claims from the other agent and makes necessary corrections",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=formatter_agent_instructions,
    tools=[]
)


def bill_report_agent_instructions(context: ReadonlyContext) -> str:
    patient_id = context.state.get("user:patient_id", "")
    return f"""You are a insurance bill report agent.
    Your customer Patient ID is: {patient_id}.
    Use the following routine to support the patient.
    1. Use the `bill_report_tool` to review the bill items
    2. Take the formatted response, For any denominations, add rupee symbol in the front and commas for readability

    If the customer asks anything else, transfer back to the triage agent.
    """

BILL_REPORT_INSTRUCTION = """
    You are a helpful policy expert. You will take bill items from the user and use the appropriate tools to verify the claim. Pass the response from the tool unchanged
"""

bill_report_agent = LlmAgent(
    name="PolicyExpertAgent",
    description="You are a helpful policy expert. You will take bill items from the user and use `rule_engine_tool` tool to verify the claim",
    instruction=bill_report_agent_instructions,
    model="gemini-2.0-flash",  # Ensure this matches your desired LLM model,
    tools=[bill_report_tool]
)
