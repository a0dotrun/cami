from cami.infra.firebase import db
from .user import User


async def get_user(user_id: str) -> User | None:
    user_ref = db.collection("users").document(user_id)
    user_doc = await user_ref.get()
    if not user_doc.exists:
        return None
    return User(**user_doc.to_dict())


async def create_user(user: User) -> None:
    user_ref = db.collection("users").document(user.id)
    await user_ref.set(user.to_dict())
