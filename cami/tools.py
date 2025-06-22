import secrets
from datetime import UTC, datetime
from typing import Literal

import firebase_admin
from firebase_admin import firestore_async
from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from cami.config import MODEL_GEMINI_2_0_FLASH, firebase_credentials
from cami.storage.policies import get_doc_from_policy
from cami.storage.report import discharge_report_template
from cami.utils.logger import logger

firebase_admin.initialize_app(firebase_credentials)


db = firestore_async.client()


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


class FieldTemplate(BaseModel):
    value: str = Field(default="")
    required: bool
    description: str
    example: str


class DischargeReportTemplate(BaseModel):
    patient_name: FieldTemplate
    address: FieldTemplate
    phone_number: FieldTemplate
    date_of_birth: FieldTemplate
    gender: FieldTemplate
    method_of_admission: FieldTemplate
    reason_for_hospitalization: FieldTemplate
    department: FieldTemplate


class PolicyPlan(BaseModel):
    name: str
    policy_id: str
    sum_insured: int


def policies_in_db() -> list[PolicyPlan]:
    policies = [
        PolicyPlan(name="Star Health Pro", policy_id="SHS1234", sum_insured=100000),
        PolicyPlan(name="Star Health Lite", policy_id="SHL7760", sum_insured=20000),
    ]
    return policies


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


# async def discharge_report(patient_id: str) -> dict:
#     """Retrieve a patient's discharge report.

#     The report contains information about which fields are required and which have already been filled out.

#     Args:
#         patient_id (str):  The unique identifier for the patient.

#     Returns:
#         dict: A dictionary containing keys:
#             - status: 'success' or 'error'.
#             - error_message: present only if error occurred.
#             - result: if successful with discharge report details.
#     """

#     def format_result(items: dict):
#         markdowns = []
#         for k, v in items.items():
#             item = f"""
#             {k}: {v["value"]}\n
#             - required: {v["required"]}\n
#             - description: {v["description"]}\n
#             \n\n
#             """
#             markdowns.append(item)
#         "".join(list(markdowns))

#     discharge_summary_ref = db.collection("discharge_summaries").document(patient_id)
#     discharge_summary_doc = await discharge_summary_ref.get()
#     if discharge_summary_doc.exists:
#         items = discharge_summary_doc.to_dict()
#         result = format_result(items)
#         print("***************** results: ", result)
#         return {"status": "success", "result": result}
#     return {
#         "status": "error",
#         "error_message": "Discharge summary report does not exists.",
#     }


# async def update_discharge_summary_field(
#     patient_id: str, field_key: str, field_value: str
# ) -> dict:
#     """Update a field in the discharge summary report for a given patient_id.

#     Args:
#         patient_id (str): The unique identifier for the patient.
#         field_key (str): The key of the field to update.
#         field_value (str): The value to set for the field.

#     Returns:
#         dict: A dictionary containing keys:
#             - status: 'success' or 'error'.
#             - error_message: present only if error occurred.
#             - result: if successful with update status of the operation.
#     """
#     logger.info(
#         f"Updating field {field_key} for patient {patient_id} with value {field_value}"
#     )
#     discharge_summary_ref = db.collection("discharge_summaries").document(patient_id)
#     discharge_summary_doc = await discharge_summary_ref.get()
#     if discharge_summary_doc.exists:
#         document_dict = discharge_summary_doc.to_dict() or {}
#         if field_key is not None and field_key in document_dict:
#             await discharge_summary_ref.update({f"{field_key}.value": field_value})
#             return {"status": "success", "result": "Field updated successfully"}
#         else:
#             return {
#                 "status": "error",
#                 "error_message": "Error updating field, the field does not exists.",
#             }
#     return {
#         "status": "error",
#         "error_message": "Discharge summary not found",
#     }


async def check_membership(patient_id: str) -> dict:
    """Check membership for the given patient_id.

    Args:
        patient_id (str): The unique identifier for the patient.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with patient membership details.
    """
    try:
        user_ref = db.collection("users").document(patient_id)
        user_doc = await user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            if user_data is None:
                return {
                    "status": "error",
                    "error_message": "Membership does not exists",
                }
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
            - result: if successful with patient membership details.
    """
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
        }
        await user_ref.set(user_data)

        # Seed data for new member
        # create a discharge summary document for the newly member
        # discharge_summary_ref = db.collection("discharge_summaries").document(patient_id)
        # await discharge_summary_ref.set(discharge_summary_template)

        return {
            "status": "success",
            "result": {
                "patient_id": patient_id,
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
            },
        }

    except Exception as e:
        logger.error(f"Error creating membership: {e!s}")
        return {
            "status": "error",
            "error_message": "Failed to create membership",
        }


# async def discharge_summary_status(patient_id: str) -> dict:
#     """Check patient's discharge summary status for the given patient_id.

#     Args:
#         patient_id (str): The unique identifier for the patient.

#     Returns:
#         dict: A dictionary containing keys:
#             - status: 'success' or 'error'.
#             - error_message: present only if error occurred.
#             - result: if successful with discharge summary status value 'pending' or 'completed'
#     """
#     try:
#         user_ref = db.collection("users").document(patient_id)
#         user_doc = await user_ref.get()

#         if user_doc.exists:
#             user_data = user_doc.to_dict()
#             if user_data is None:
#                 return {"status": "error", "error_message": "Patient does not exists."}
#             return {
#                 "status": "success",
#                 "result": user_data["discharge_summary_report"],
#             }
#         else:
#             return {"status": "error", "error_message": "Patient does not exists."}
#     except Exception as e:
#         logger.error(f"Error checking membership for patient {patient_id}: {e!s}")
#         return {
#             "status": "error",
#             "error_message": "Error when checking for discharge summary status",
#         }


# async def update_discharge_summary_status(patient_id: str, status: str) -> dict:
#     """Update patient's discharge summary status for the given patient_id.

#     Args:
#         patient_id (str): The unique identifier for the patient.
#         status (str): The status of the discharge summary either 'completed' or 'pending'

#     Returns:
#         dict: A dictionary containing keys:
#             - status: 'success' or 'error'.
#             - error_message: present only if error occurred.
#             - result: if successful with update status of the operation.
#     """
#     try:
#         user_ref = db.collection("users").document(patient_id)
#         user_doc = await user_ref.get()

#         if not user_doc.exists:
#             return {"status": "error", "error_message": "Patient does not exist."}

#         # Update the discharge_summary_report field
#         await user_ref.update({"discharge_summary_report": status})

#         return {
#             "status": "success",
#             "result": f"Successfully updated discharge summary status report to {status}",
#         }
#     except Exception as e:
#         logger.error(
#             f"Error updating discharge summary status for patient {patient_id}: {e!s}"
#         )
#         return {
#             "status": "error",
#             "error_message": "Error when updating discharge summary status",
#         }


def available_policies() -> dict:
    """List available policies for purchase.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful list of policies for purchase.
    """
    logger.info("Listing available policies for purchase")
    policies = policies_in_db()
    items: list[str] = []
    for policy in policies:
        i = f"""\n
        - Name: {policy.name}\n - Policy ID: {policy.policy_id}\n - Sum Assured: {policy.sum_insured}\n\n"""
        items.append(i)
    items_str = "".join(items)
    return {
        "status": "success",
        "result": f"""Policies:
        {items_str}
        """,
    }


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
    try:
        policies = policies_in_db()
        selected_policy = next((p for p in policies if p.policy_id == policy_id), None)
        if selected_policy is None:
            return {
                "status": "error",
                "error_message": "The selected Policy does not exist or expired. Please select another policy.",
            }
        policy_ref = db.collection("policies").document(patient_id)
        await policy_ref.set(
            {
                "policy_id": selected_policy.policy_id,
                "name": selected_policy.name,
                "date_of_purchase": datetime.now(),
            }
        )
        return {
            "status": "success",
            "result": f"Successfully purchased policy {selected_policy.name} having policy ID {selected_policy.policy_id}",
        }

    except Exception as e:
        logger.error(f"Error purchasing policy plan: {e!s}")
        return {
            "status": "error",
            "error_message": "Error purchasing policy. Please try again.",
        }


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
    try:
        policy_ref = db.collection("policies").document(patient_id)
        policy_doc = await policy_ref.get()
        if not policy_doc.exists:
            return {
                "status": "error",
                "error_message": "No existing policy found for the patient. Please purchase a new policy.",
            }

        selected_policy = policy_doc.to_dict()
        if selected_policy is None:
            return {
                "status": "error",
                "error_message": "No existing policy found for the patient. Please purchase a new policy.",
            }
        return {
            "status": "success",
            "result": f"Found existing policy {selected_policy.get('name')} having policy ID {selected_policy.get('policy_id')}",
        }

    except Exception as e:
        logger.error(f"Error checking existing policy: {e!s}")
        return {
            "status": "error",
            "error_message": "Error checking existing policy. Please try again.",
        }


def policy_faq_instructions(context: ReadonlyContext) -> str:
    policy_id = context.state.get("temp:policy_id", "")
    document = get_doc_from_policy(policy_id)

    return f"""You are an FAQ agent speaking to a customer.
    <PolicyDocument>
        {document}
    </PolicyDocument>

    Use the following routine to support the customer.
    1. Respond to the customer with the answer based on Policy document.
    2. If you do not know the answer, politely inform the customer that you do not have the information.
    3. Do not make up your own answers and Do not provide any information that is not in the document.
    """


policy_faq_agent = Agent(
    name="policy_faq_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction=policy_faq_instructions,
    tools=[],
)


async def policy_faqs(policy_id: str, query: str, tool_context: ToolContext) -> dict:
    """Lookup answers to Frequency Asked Questions (FAQs) for a Policy.

    Args:
        policy_id (str): Policy ID
        query (str): The question or query about the policy.

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with the answer to the query.
    """
    tool_context.state["temp:policy_id"] = policy_id
    agent_tool = AgentTool(agent=policy_faq_agent)
    result = await agent_tool.run_async(
        args={"request": query},
        tool_context=tool_context,
    )
    return {
        "status": "success",
        "result": result,
    }


class Claim(BaseModel):
    status: Literal["ongoing", "completed", "expired"]
    discharge_report_status: Literal["pending", "completed"]
    treatment_report_status: Literal["pending", "completed"]
    started_on: datetime
    discharge_report: DischargeReportTemplate


async def check_ongoing_claim(patient_id: str) -> dict:
    """Check if there is an ongoing claim for the patient.

    Args:
        patient_id (str): Patient's ID

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with ongoing claim details.
    """
    print("**************** CHECK ONGOING CLAIM ****************")
    logger.info(f"Checking existing policy for patient {patient_id}")
    print("**************** CHECK ONGOING CLAIM ****************")

    def format_result(claim: Claim) -> str:
        return f"""Claim Status: {claim.status}
        Discharge Report Status: {claim.discharge_report_status}
        Treatment Report Status: {claim.treatment_report_status}
        Started On: {claim.started_on.strftime("%Y-%m-%d %H:%M:%S")}
        """

    try:
        claim_ref = db.collection("claims").document(patient_id)
        claim_doc = await claim_ref.get()
        if not claim_doc.exists:
            return {
                "status": "error",
                "error_message": "No existing claim found for the patient. Please start a new claim.",
            }

        selected_claim = claim_doc.to_dict()
        if selected_claim is None:
            return {
                "status": "error",
                "error_message": "No existing claim found for the patient. Please start a new claim.",
            }
        # claim exists, format the result
        claim = Claim(**selected_claim)
        return {
            "status": "success",
            "result": format_result(claim),
        }

    except Exception as e:
        logger.error(f"Error checking claim: {e!s}")
        return {
            "status": "error",
            "error_message": "Error checking existing claim. Please try again.",
        }


async def start_claim(patient_id: str) -> dict:
    """Start a new Claim for the Patient.

    Args:
        patient_id (str): Patient's ID

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with ongoing claim details.
    """
    print("**************** START A NEW CLAIM ****************")
    logger.info(f"Starting new claim for patient {patient_id}")
    print("**************** START A NEW CLAIM ****************")

    def format_result(claim: Claim) -> str:
        return f"""Claim Status: {claim.status}
        Discharge Report Status: {claim.discharge_report_status}
        Treatment Report Status: {claim.treatment_report_status}
        Started On: {claim.started_on.strftime("%Y-%m-%d %H:%M:%S")}
        """

    try:
        claim_ref = db.collection("claims").document(patient_id)

        # Prepare claim document
        claim = Claim(
            status="ongoing",
            discharge_report_status="pending",
            treatment_report_status="pending",
            started_on=datetime.now(UTC),
            discharge_report=DischargeReportTemplate(**discharge_report_template),
        )
        await claim_ref.set(claim.model_dump())

        return {
            "status": "success",
            "result": format_result(claim),
        }

    except Exception as e:
        logger.error(f"Error creating claim: {e!s}")
        return {
            "status": "error",
            "error_message": "Error creating claim. Please try again.",
        }


async def discharge_report_status(patient_id: str) -> dict:
    """Check Discharge Report Status for the Patient.

    Args:
        patient_id (str): Patient's ID

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful status of the discharge report ('pending' or 'completed').
    """
    logger.info(f"Checking discharge report status for patient {patient_id}")

    try:
        claim_ref = db.collection("claims").document(patient_id)
        claim_doc = await claim_ref.get()
        if not claim_doc.exists:
            return {
                "status": "error",
                "error_message": "No existing claim to check for disharge report status. Please start a new claim.",
            }

        selected_claim = claim_doc.to_dict()
        if selected_claim is None:
            return {
                "status": "error",
                "error_message": "No existing claim to check for disharge report status. Please start a new claim.",
            }
        claim = Claim(**selected_claim)
        return {
            "status": "success",
            "result": f"Discharge Report Status: {claim.discharge_report_status}",
        }
    except Exception as e:
        logger.error(f"Error checking claim: {e!s}")
        return {
            "status": "error",
            "error_message": "Error discharge report status. Please try again.",
        }


async def discharge_report_form(patient_id: str) -> dict:
    """Return the Discharge Report Form to be filled by the Patient.

    Args:
        patient_id (str): Patient's ID

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with discharge report form fields.
    """
    logger.info(f"Checking existing policy for patient {patient_id}")

    def format_result(claim: Claim) -> str:
        markdown_output = []
        markdown_output.append("# Discharge Report Form Fields:\n")
        discharge_report_instance = claim.discharge_report
        for field_name, _ in DischargeReportTemplate.model_fields.items():
            field_template_instance: FieldTemplate = getattr(discharge_report_instance, field_name)
            markdown_output.appen(f"## {field_name}:")
            field_data = field_template_instance.model_dump()
            markdown_output.append(f" - required: {field_data['required']}")
            markdown_output.append(f' - value: "{field_data["value"]}"')
            markdown_output.append(f' - description: "{field_data["description"]}"')
            markdown_output.append(f' - example: "{field_data["example"]}"')

            markdown_output.append("\n")

        return "\n".join(markdown_output)

    try:
        claim_ref = db.collection("claims").document(patient_id)
        claim_doc = await claim_ref.get()
        if not claim_doc.exists:
            return {
                "status": "error",
                "error_message": "No existing claim found for Discharge Report Form. Please start a new claim.",
            }

        selected_claim = claim_doc.to_dict()
        if selected_claim is None:
            return {
                "status": "error",
                "error_message": "No existing claim found for Discharge Report Form. Please start a new claim.",
            }
        # claim exists, format the result
        claim = Claim(**selected_claim)
        return {
            "status": "success",
            "result": format_result(claim),
        }

    except Exception as e:
        logger.error(f"Error checking claim: {e!s}")
        return {
            "status": "error",
            "error_message": "Error checking existing claim. Please try again.",
        }


async def update_discharge_report_form_field(patient_id: str, field: str, value: str) -> dict:
    """Start a new Claim for the Patient.

    Args:
        patient_id (str): Patient's ID
        field (str): Field to update
        value (str): The value of the field

    Returns:
        dict: A dictionary containing keys:
            - status: 'success' or 'error'.
            - error_message: present only if error occurred.
            - result: if successful with update status of the field
    """
    logger.info(f"Update discharge form field: {field}:{value} for patient ID: {patient_id}")

    try:
        claim_ref = db.collection("claims").document(patient_id)
        full_qualified_field = f""

        await claim_ref.set(claim.model_dump())

        return {
            "status": "success",
            "result": format_result(claim),
        }

    except Exception as e:
        logger.error(f"Error creating claim: {e!s}")
        return {
            "status": "error",
            "error_message": "Error creating claim. Please try again.",
        }
