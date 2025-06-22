import os
from google.adk.agents.readonly_context import ReadonlyContext


def bill_eligibility_agent_instructions(context: ReadonlyContext) -> str:
    bill_items = context.state.get('claim:bill_items', [])
    print("Bill Items from the stats: {}".format(bill_items))

    policy_doc_path = os.path.join(os.getcwd(), "cami/storage/policy-lite.md")
    print("Policy Path: {}".format(policy_doc_path))

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
            
            Respond with the list of bill items with following fields in JSON format. 
                - name
                - amount
                - eligible
                - reason 
            
            The output should be only JSON and json alone, no extra text or code delimiters. output should start with [ and end with ] 
        """

    print("Prepared Policy Doc: {}".format(instruction))
    return instruction
