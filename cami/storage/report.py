discharge_report_template: dict[str, dict] = {
    "patient_name": {
        "value": "",
        "required": True,
        "description": "The patient's full legal name, including first and last name.",
        "example": "John Doe",
    },
    "address": {
        "value": "",
        "required": True,
        "description": "The patient's complete mailing address.",
        "example": "123 Main Street, Any town, ST 12345",
    },
    "phone_number": {
        "value": "",
        "required": True,
        "description": "The patient's primary contact phone number, including the country code. Default country code is IND +91",
        "example": "+1-555-123-4567",
    },
    "date_of_birth": {
        "value": "",
        "required": True,
        "description": "The patient's date of birth in YYYY-MM-DD format.",
        "example": "1990-06-15",
    },
    "gender": {
        "value": "",
        "required": True,
        "description": "The patient's gender.",
        "example": """ "Male", "Female", "Other" """,
    },
    "method_of_admission": {
        "value": "",
        "required": True,
        "description": "The method by which the patient was admitted to the hospital.",
        "example": """ "Elective", "Emergency", "Transfer", "Newborn", "Other" """,
    },
    "reason_for_hospitalization": {
        "value": "",
        "required": True,
        "description": "A brief description of the primary medical reason, chief complaint, or symptoms leading to hospitalization.",
        "example": "Patient presented with severe chest pain and shortness of breath.",
    },
    "department": {
        "value": "",
        "required": False,
        "description": "The specific hospital department the patient was admitted to.",
        "example": "Cardiology",
    },
}
