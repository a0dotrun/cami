from google.adk.agents import LlmAgent
from cami.rule_engine import rule_engine_tool

from cami.agents import triage_agent

root_agent = triage_agent

# For testing rule_engine directly
# root_agent = LlmAgent(
#     name="PolicyExpertAgent",
#     instruction="You are a helpful policy expert. You will take bill items from the user and use the appropriate tools to verify the claim",
#     model="gemini-2.0-flash",  # Ensure this matches your desired LLM model,
#     tools=[rule_engine_tool]
# )
