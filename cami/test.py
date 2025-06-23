import asyncio

from google.adk.agents import LlmAgent
from google.adk.cli.cli import run_input_file
from google.adk.runners import InMemoryRunner, InvocationContext, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types

from cami.rule_engine import rule_engine_tool

APP_NAME = "summary_agent"
USER_ID = "user1234"
SESSION_ID = "1234"
claim = {
    "patient": "Kireeti",
    "hospital": "Jupiter Hospital and Institute of Vascular Surgery, No.28, 7th Main, 9th Cross, Malleswaram, Bangalore, 560003",
    "procedure": "Kidney Dialysis",
    "total_bills": 398300,
    "bill_items": [
        {"name": "Dialysis", "amount": 350000},
        {"name": "Injections", "amount": 6000},
        {"name": "Blood Work", "amount": 7800},
        {"name": "Nose Surgery", "amount": 34500},
    ],
}

# --- 2. Initialize your LlmAgent ---
# We'll initialize it with a generic instruction initially, then update it per run.
my_agent = LlmAgent(
    name="PolicyExpertAgent",
    instruction="You are a helpful policy expert. You will take bill items from the user and use the appropriate tools to verify the claim",
    model="gemini-2.0-flash",  # Ensure this matches your desired LLM model,
    tools=[rule_engine_tool],
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=my_agent, app_name=APP_NAME, session_service=session_service)


# --- 3. Prepare Input and ToolContext (if needed) ---
# The input query you want to test
user_query = "What is the coverage for dialysis and what about room rent?"

# Create a ToolContext instance and set the policy ID
# initial_tool_context = ToolContext()


def call_agent(query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


if __name__ == "__main__":
    print(call_agent(user_query))
