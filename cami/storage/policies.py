def get_doc_from_policy(policy_id: str) -> str:
    docs = {
        "SHL7760": "",
        "SHS1234": "",
    }
    doc = docs.get(policy_id)
    if doc is None:
        return "No document found for the given policy ID."
    return doc
