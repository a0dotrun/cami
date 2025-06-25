from cami.infra.firebase import db
from .policy import Policy, CamiLitePolicy, CamiProPolicy
from .patient_policy import PatientPolicy


async def list_policies() -> list:
    return [CamiLitePolicy, CamiProPolicy]


async def get_patient_policy(patient_id: str) -> PatientPolicy | None:
    policy_ref = db.collection("policies").document(patient_id)
    policy_doc = await policy_ref.get()
    if not policy_doc.exists:
        return None
    return PatientPolicy(**policy_doc.to_dict())


async def add_patient_policy(patient_id: str, patient_policy: PatientPolicy) -> None:
    await db.collections("policies").document(patient_id).set(patient_policy.to_dict())


async def update_patient_policy(policy: Policy):
    await db.collection("policies").document(policy.id).update(policy)
