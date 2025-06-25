from . import db as policy_db_utils
from .policy import get_policy_by_id
from .patient_policy import PatientPolicy
from cami.utils import logger, tool_error_handler, error, success


@tool_error_handler("Unable to fetch available policies at this time")
async def available_policies() -> dict:
    """List available policies for purchase.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful list of policies for purchase.
    """
    logger.info("Listing available policies for purchase")
    policies = await policy_db_utils.list_policies()

    msg = "Policies:"
    for policy in policies:
        msg += f"""\n
            <Policy>
                *Name:* {policy.name} 
                *Policy ID:* {policy.policy_id} 
                *Sum Insured:* {policy.sum_insured}
            </Policy>
            """

    return success(msg)


@tool_error_handler("Error purchasing policy. Please try again.")
async def purchase_policy(patient_id: str, policy_id: str) -> dict:
    """Create a new policy for the patient with the selected policy plan.

    Args:
        patient_id (str): Patient's ID
        policy_id (str): Selected policy ID by the Patient

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with purchased policy details.
    """
    logger.info(f"Purchasing policy {policy_id} for patient {patient_id}")
    policy = get_policy_by_id(policy_id)
    await policy_db_utils.add_patient_policy(patient_id, policy.id)
    return success(f"Successfully purchased policy {policy.name} having policy ID {policy.policy_id}")


@tool_error_handler("Error checking existing policy. Please try again.")
async def check_existing_policy(patient_id: str) -> dict:
    """Check existing policy for the Patient.

    Args:
        patient_id (str): Patient's ID

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with purchased policy details.
    """

    logger.info(f"Checking existing policy for patient {patient_id}")
    policy = await policy_db_utils.get_patient_policy(patient_id)
    if policy is None:
        return error("No existing policy found for the patient. Please purchase a new policy.")

    # Todo: What is the right format, to share info with LLM?
    return success(f"Found existing policy {policy.name} having policy ID {policy.policy_id}")
