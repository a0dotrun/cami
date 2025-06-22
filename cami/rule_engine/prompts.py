from google.adk.agents.readonly_context import ReadonlyContext


def bill_eligibility_agent_instructions(context: ReadonlyContext) -> str:
    bill_items = context.state.get('bill_items', [])

    policy_doc_path = "./storage/policy-lite.md"
    instruction = f"""
        You are an insurance agent to review the claim for individual bill items and determine their eligibility.
        
        <BillItems>
            {bill_items}
        </BillItems>
    """
    with open(policy_doc_path) as f:
        doc = f.read()
        instruction += f"""
            <PolicyDocument>
                {doc}
            </PolicyDocument>
            
            Respond with the list of bill items with following fields and nothing else.
                - name
                - amount
                - eligible
                - reason 
        """
    return doc
