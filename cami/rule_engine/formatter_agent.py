from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext

from cami.config import MODEL_GEMINI_2_0_FLASH


def formatter_agent_instructions(context: ReadonlyContext) -> str:
    rule_engine_output = context.state.get("claim:rule_engine_output", [])

    instruction = f"""
        You are a Markdown table formatter. Your task is to convert the provided array of items into a well-formatted Markdown table.

        **Your output must contain ONLY the Markdown table and absolutely no other text, explanations, or conversational filler.**
        
        The table must include a header row derived from the keys of the items, and each item should be a row in the table. Ensure all values are presented clearly.
        
        **Do not include any additional text, introductory sentences, concluding remarks, or explanations whatsoever (e.g., "Here is a summary...", "Please review the details...", "Do you have any questions about the claim?").**
        
        <Input>
            {rule_engine_output}
        </Input>
    """

    print(f"Markdown instruction of approvals: {instruction}")
    return instruction


output_formatter_agent = Agent(
    name="review_agent",
    description="You are a formatter agent, that takes JSON input and outputs only markdown table of claims",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=formatter_agent_instructions,
    tools=[],
)
