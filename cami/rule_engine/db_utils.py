from cami.tools import db


async def get_patient_info(patient_id) -> dict:
    user_ref = db.collection("users").document(patient_id)
    user_doc = await user_ref.get()

    policies_ref = db.collection("policies").document(patient_id)
    policies_doc = await policies_ref.get()

    claim_ref = db.collection("claims").document(patient_id)
    claims_doc = await claim_ref.get()

    print("User Document:", user_doc)
    print("Policies Document:", policies_doc)
    print("Claims Document:", claims_doc)

    policy_id = policies_doc.get("policy_id")

    return {
        "user_name": f"{user_doc.get('first_name')} {user_doc.get('last_name')}",
        "policy_id": policy_id,
        "age": claims_doc.get("discharge_report").get("age", {}).get("value", 0),
        "hospitalisation_days": claims_doc.get("discharge_report")
        .get("hospitalization_days", {})
        .get("value", 0),
        "sum_insured": 500000
        if policy_id == "CAMI2025-Lite"
        else 1000000,  # Todo: Change the hardcoded values
        "hospital_in_network": "Non-Network",
    }
