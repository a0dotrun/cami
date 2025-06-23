from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext

from cami.config import MODEL_GEMINI_2_0_FLASH


def formatter_agent_instructions(context: ReadonlyContext) -> str:
    rule_engine_output = context.state.get("claim:rule_engine_output", [])

    instruction = f"""
        You are a Markdown table formatter. Your task is to convert the provided array of items into a well-formatted Markdown table.
        The table must include a header row derived from the keys of the items, and each item should be a row in the table.
        Ensure all values are presented clearly.
        <Input>
            {rule_engine_output}
        </Input>
        
        Your output should be *only* the Markdown table, with no additional text, explanations, or code block delimiters (e.g., ```).
    """

    print(f"Markdown instruction of approvals: {instruction}")
    return instruction


output_formatter_agent = Agent(
    name="review_agent",
    description="A helpful insurance agent, that reviews the processed claims from the other agent and makes necessary corrections",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=formatter_agent_instructions,
    tools=[],
)
