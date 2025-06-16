import secrets
from datetime import UTC, datetime

from firebase_admin import firestore_async

from cami.utils.logger import logger

db = firestore_async.client()


# from typing import Any


# class AskForApproval:
#     """
#     Request approval for a reimbursement from the designated approver.

#     Args:
#         amount (float): The amount requested.
#         purpose (str): The reason for the reimbursement.

#     Returns:
#         A dictionary containing the approval status and metadata:
#             status (str): The current status (e.g., "pending").
#             approver (str): The name of the approver handling the request.
#             message (str): A human-readable message about the request status.
#     """

#     name = "ask_for_approval"

#     def __init__(self):
#         pass

#     async def __call__(self, amount: float, purpose: str) -> dict[str, Any]:
#         print("-> [In Tool] args:", amount, purpose)
#         return {
#             "status": "pending",
#             "approver": "Sean Zhou",
#             "message": "Your request is being processed. Please wait.",
#         }

#     @property
#     def __name__(self):
#         return self.name


# class GetClaimStatus:
#     """
#     Returns claim approval status for a reimbursement from the designated approver.

#     Returns:
#         A dictionary containing the approval status and metadata:
#             status (str): The current status (e.g., "success").
#             claims (list): List of claims with keys: purpose, amount, status
#     """

#     name = "get_approval_status"

#     def __init__(self):
#         pass

#     async def __call__(
#         self,
#     ) -> dict[str, Any]:
#         return {
#             "status": "success",
#             "claims": [],
#         }

#     @property
#     def __name__(self):
#         return self.name


discharge_summary_template: dict[str, dict] = {
    "patient_name": {
        "value": "[Enter patient's full name]",
        "required": True,
        "description": "The patient's full legal name, including first and last name.",
        "example": "John Doe",
    },
    "address": {
        "value": "[Enter patient's full address]",
        "required": True,
        "description": "The patient's complete mailing address.",
        "example": "123 Main Street, Any town, ST 12345",
    },
    "phone_number": {
        "value": "[Enter phone number]",
        "required": True,
        "description": "The patient's primary contact phone number, including the country code. Default country code is IND +91",
        "example": "+1-555-123-4567",
    },
    "date_of_birth": {
        "value": "[Enter date of birth]",
        "required": True,
        "description": "The patient's date of birth in YYYY-MM-DD format.",
        "example": "1990-06-15",
    },
    "gender": {
        "value": "[Select gender]",
        "required": True,
        "description": "The patient's gender.",
        "choices": ["Male", "Female", "Other", "Prefer not to say"],
    },
    "method_of_admission": {
        "value": "[Select admission method]",
        "required": True,
        "description": "The method by which the patient was admitted to the hospital.",
        "choices": ["Elective", "Emergency", "Transfer", "Newborn", "Other"],
    },
    "reason_for_hospitalization": {
        "value": "[Describe the reason for hospitalization]",
        "required": True,
        "description": "A brief description of the primary medical reason, chief complaint, or symptoms leading to hospitalization.",
        "example": "Patient presented with severe chest pain and shortness of breath.",
    },
    "department": {
        "value": "[Optional: Enter department]",
        "required": False,
        "description": "The specific hospital department the patient was admitted to.",
        "example": "Cardiology",
    },
}


# async def discharge_summary_report(patient_id: str) -> dict:
#     """Checks if a patient's discharge summary report is 'completed' or 'pending'.

#     This tool takes a patient ID and returns the status of their discharge summary.
#     It does not return the content of the summary itself.

#     Args:
#         patient_id (str): The unique identifier for the patient (e.g., "PID-12345").

#     Returns:
#         dict: A dictionary with two keys:
#               - 'status': The status of the tool call ('success' or 'error').
#               - 'report': The status of the discharge summary ('completed' or 'pending')
#                          OR an error message if the tool call failed.

#               - Example (Pending):
#                 {"status": "success", "report": "pending"}
#               - Example (Completed):
#                 {"status": "success", "report": "completed"}
#               - Example (Error):
#                 {"status": "error", "error_message": "Patient ID 'PID-99999' not found."}
#     """
#     logger.info(
#         "[Tool Called: discharge_summary_report] with args: patient_id='%s'",
#         patient_id,
#     )

#     return {"status": "success", "report": "pending"}


async def discharge_summary_report(patient_id: str) -> dict:
    """Retrieve a patient's discharge summary report.

    The report contains information about which fields are required and which have already been filled out.

    Args:
        patient_id (str):  The unique identifier for the patient.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with discharge summary details.
    """
    discharge_summary_ref = db.collection("discharge_summaries").document(patient_id)
    discharge_summary_doc = await discharge_summary_ref.get()
    if discharge_summary_doc.exists:
        return {"status": "success", "result": discharge_summary_doc.to_dict()}
    return {
        "status": "error",
        "error_message": "Discharge summary report does not exists.",
    }


async def update_discharge_summary_field(patient_id: str, field_key: str, field_value: str) -> dict:
    """Update a field in the discharge summary report for a given patient_id.

    Args:
        patient_id (str): The unique identifier for the patient.
        field_key (str): The key of the field to update.
        field_value (str): The value to set for the field.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with update status of the operation.
    """
    logger.info(f"Updating field {field_key} for patient {patient_id} with value {field_value}")
    discharge_summary_ref = db.collection("discharge_summaries").document(patient_id)
    discharge_summary_doc = await discharge_summary_ref.get()
    if discharge_summary_doc.exists:
        document_dict = discharge_summary_doc.to_dict() or {}
        if field_key is not None and field_key in document_dict:
            await discharge_summary_ref.update({f"{field_key}.value": field_value})
            return {"status": "success", "result": "Field updated successfully"}
        else:
            return {
                "status": "error",
                "error_message": "Error updating field, the field does not exists.",
            }
    return {
        "status": "error",
        "error_message": "Discharge summary not found",
    }


async def check_membership(patient_id: str) -> dict:
    """Check membership for the given patient_id.

    Args:
        patient_id (str): The unique identifier for the patient.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with user details.
    """
    try:
        user_ref = db.collection("users").document(patient_id)
        user_doc = await user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            if user_data is None:
                return {"status": "error", "error_message": "Membership does not exists"}
            return {
                "status": "success",
                "result": {
                    "patient_id": patient_id,
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                },
            }
        else:
            return {
                "status": "error",
                "error_message": "User does not exists. Please create membership first",
            }
    except Exception as e:
        logger.error(f"Error checking membership for patient {patient_id}: {e!s}")
        return {
            "status": "error",
            "error_message": f"Failed to check membership: {e!s}",
        }


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
            - result: if successful with creation status of the operation.
    """
    logger.info(f"Creating membership for patient {first_name} {last_name} with email {email}")

    try:
        random_str = "".join(secrets.choice("0123456789") for _ in range(6))
        patient_id = f"PID-{random_str}"

        # Create the user document
        user_ref = db.collection("users").document(patient_id)

        # Prepare user data with other properties
        user_data = {
            "phone_number": phone_number,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "discharge_summary_report": "pending",
        }
        await user_ref.set(user_data)

        # Seed data for new member
        # create a discharge summary document for the newly member
        discharge_summary_ref = db.collection("discharge_summaries").document(patient_id)
        await discharge_summary_ref.set(discharge_summary_template)

        return {"status": "success", "result": f"member created with patient id: {patient_id}"}

    except Exception as e:
        logger.error(f"Error creating membership: {e!s}")
        return {
            "status": "error",
            "error_message": "Failed to create membership",
        }


async def discharge_summary_status(patient_id: str) -> dict:
    """Check patient's discharge summary status for the given patient_id.

    Args:
        patient_id (str): The unique identifier for the patient.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with discharge summary status value 'pending' or 'completed'
    """
    try:
        user_ref = db.collection("users").document(patient_id)
        user_doc = await user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            if user_data is None:
                return {"status": "error", "error_message": "Patient does not exists."}
            return {"status": "success", "result": user_data["discharge_summary_report"]}
        else:
            return {"status": "error", "error_message": "Patient does not exists."}
    except Exception as e:
        logger.error(f"Error checking membership for patient {patient_id}: {e!s}")
        return {
            "status": "error",
            "error_message": "Error when checking for discharge summary status",
        }


async def update_discharge_summary_status(patient_id: str, status: str) -> dict:
    """Update patient's discharge summary status for the given patient_id.

    Args:
        patient_id (str): The unique identifier for the patient.
        status (str): The status of the discharge summary either 'completed' or 'pending'

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with update status of the operation.
    """
    try:
        user_ref = db.collection("users").document(patient_id)
        user_doc = await user_ref.get()

        if not user_doc.exists:
            return {"status": "error", "error_message": "Patient does not exist."}

        # Update the discharge_summary_report field
        await user_ref.update({"discharge_summary_report": status})

        return {
            "status": "success",
            "result": f"Successfully updated discharge summary status report to {status}",
        }
    except Exception as e:
        logger.error(f"Error updating discharge summary status for patient {patient_id}: {e!s}")
        return {
            "status": "error",
            "error_message": "Error when updating discharge summary status",
        }
