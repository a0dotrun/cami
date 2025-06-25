import datetime

from cami.infra.firebase import db
from .policy import Policy, CamiLitePolicy, CamiProPolicy, get_policy_by_id
from cami.user_policy import UserPolicy


async def list_policies() -> list:
    return [CamiLitePolicy, CamiProPolicy]


async def get_user_policy(user_id: str) -> UserPolicy | None:
    policy_ref = db.collection("policies").document(user_id)
    policy_doc = await policy_ref.get()
    if not policy_doc.exists:
        return None
    return UserPolicy(**policy_doc.to_dict())


async def add_user_policy(user_id: str, policy_id: str) -> None:
    dop = datetime.timedelta(days=365)
    valid_till = dop + datetime.timedelta(days=365)
    policy = get_policy_by_id(policy_id)

    user_policy = UserPolicy(
        id=user_id,
        policy_id=policy_id,
        date_of_purchase=dop,
        valid_till=valid_till,
        sum_insured=policy.sum_insured
    )
    await db.collections("policies").document(user_id).set(user_policy.to_dict())


async def update_user_policy(policy: Policy):
    await db.collection("policies").document(policy.id).update(policy)
