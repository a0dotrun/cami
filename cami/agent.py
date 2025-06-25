from google.adk.agents import Agent

from cami.config import MODEL_GEMINI_2_0_FLASH
from cami.user.tools import (check_membership, create_membership)
from cami.agents import claim_agent
from cami.policy import policy_agent, on_after_membership_tool, check_existing_policy


TRIAGE_INSTRUCTION = """You are a helpful customer service and triaging agent. You can use your tools and delegate customer's request to the appropriate agent.
Note: users, customers, and members are references for patients.
If you are speaking to a patient, use the following routine to support the patient.
1. If you haven't already greeted the patient, welcome them to Cami, Insurance Claim Assistant Agent.
2. Ask for their patient ID if you don't already know it. They must either provide an ID, or sign up for new membership.
3. Use the check membership tool to lookup patient and thank them for becoming a member. Do not rely on your own knowledge.
4. Use the create membership tool to create the patient membership. Make sure the patient is registered before proceeding with any customer's requests.
5. If the patient asks about claiming insurance or similar request, make sure they have an existing policy, otherwise delegate to the policy agent.
6. Review patient's request and delegate to appropriate agent.
"""

root_agent = Agent(
    name="triage_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=TRIAGE_INSTRUCTION,
    description="Main customer service and triaging agent.",
    sub_agents=[],
    tools=[check_membership, create_membership],
    after_tool_callback=on_after_membership_tool,
)

# For testing rule_engine directly
# from cami.rule_engine.local import bill_report_agent
# root_agent = bill_report_agent
