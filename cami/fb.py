import asyncio

from policy.db import *
from policy.policy import *
from policy.patient_policy import *


async def main():
    # await db.collection("users").document("alan_turing").set({
    #     'date_of_birth': 'June 23, 1912',
    #     'full_name': 'Alan Turing'
    # })

    patient_id = "PID-183747"
    # patient_policy = PatientPolicy(
    #     patient_id=patient_id,
    #     policy_id=CamiLitePolicy.id,
    #     date_of_purchase=datetime.datetime.now(),
    # )
    # await db.collection("policies").document(patient_id).set(patient_policy.to_dict())

    ref = db.collection("policies").document(patient_id)
    doc = await ref.get()
    print(doc.to_dict())


if __name__ == "__main__":
    asyncio.run(main())
