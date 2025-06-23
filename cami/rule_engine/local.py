from google.adk.agents import Agent, LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

from .tools import bill_report_tool


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
    model="gemini-2.0-flash",
    tools=[bill_report_tool],
)
