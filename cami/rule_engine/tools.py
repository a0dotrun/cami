# import json

from google.adk.agents import Agent

# # from google.adk.tools.agent_tool import AgentTool
# # from google.adk.tools.tool_context import ToolContext
from cami.config import MODEL_GEMINI_2_0_FLASH

from .prompts import prcess_claim_instructions

process_claim_agent = Agent(
    name="process_claim_agent",
    description="Process claim agent is agent handling the processing of the claim after all the pending reports are completed.",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=prcess_claim_instructions,
)


# def response_formatter(bill_items):
#     response = ""
#     for item in bill_items:
#         response += f"""
#             **{item["name"]}**
#             Claimed Amount: {item["claimed_amount"]}
#             Approved Amount: {item["approved_amount"]}
#             Reason: {item["reason"]}
#         """
#     return response


# async def process_claim(patient_id: str, tool_context: ToolContext) -> str:
#     """Verify the bill items claim against the policy document.

#     Args:
#         patient_id (str): The unique identifier for the patient.

#     Returns:
#         str: Markdown formatted bill items report for user review
#     """
#     bill_items = claim.get("bill_items", [])
#     tool_context.state["claim:bill_items"] = bill_items
#     agent_tool = AgentTool(agent=bill_eligibility_agent)
#     result = await agent_tool.run_async(
#         args={"request": "claims from user"},  # Todo: What should we send?
#         tool_context=tool_context,
#     )
#     cleaned_result = result.replace("\n", "").strip("```").strip("json")
#     cleaned_result = json.loads(cleaned_result)
#     print("Cleaned Result from AgentTool ", cleaned_result)

#     formatted_response = response_formatter(cleaned_result)
#     print("Formatted Response:", formatted_response)
#     return formatted_response
