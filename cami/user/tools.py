import secrets
from datetime import UTC, datetime

from cami.utils import logger, tool_error_handler, success, error
from . import db as db_utils
from .user import User


@tool_error_handler("Failed to check membership")
async def check_membership(user_id: str) -> dict:
    """Check membership for the given yser_id.

    Args:
        user_id (str): The unique identifier for the patient.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with patient membership details.
    """
    logger.info(f"Checking membership for user {user_id}")
    user = await db_utils.get_user(user_id)
    if user is None:
        return error("Membership does not exists")

    return success(user.to_dict())


@tool_error_handler("Failed to create membership")
async def create_membership(first_name: str, last_name: str, phone_number: str, email: str) -> dict:
    """Create a new patient membership with the given information.

    Args:
        first_name (str): Patient's first name
        last_name (str): Patient's last name
        phone_number (str): Patient's phone number
        email (str): Patient's email address

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with patient membership details.
    """

    logger.info(f"Creating membership for user {email}")
    random_str = "".join(secrets.choice("0123456789") for _ in range(6))
    user = User(
        id=f"UID-{random_str}",
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    await db_utils.create_user(user)

    return {
        "status": "success",
        "result": {
            "patient_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }
