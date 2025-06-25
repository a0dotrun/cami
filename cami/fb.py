import asyncio

from policy.db import *
from policy.policy import *
from cami.user_policy import *


async def main():
    # await db.collection("users").document("alan_turing").set({
    #     'date_of_birth': 'June 23, 1912',
    #     'full_name': 'Alan Turing'
    # })

    patient_id = "PID-183747"
    # user_policy = UserPolicy(
    #     patient_id=patient_id,
    #     policy_id=CamiLitePolicy.id
    # )
    # await db.collection("policies").document(patient_id).set(user_policy.to_dict())

    ref = db.collection("policies").document(patient_id)
    doc = await ref.get()
    print(doc.to_dict())


if __name__ == "__main__":
    asyncio.run(main())
