discharge_report_template: dict[str, dict] = {
    "hospital_name": {
        "value": "",
        "required": True,
        "description": "The name of the hospital the Patient was addmitted to.",
        "example": "Penn State Medical College",
    },
    "address": {
        "value": "",
        "required": True,
        "description": "The patient's complete mailing address.",
        "example": "123 Main Street, Any town, ST 12345",
    },
    "age": {
        "value": "",
        "required": True,
        "description": "The Patient's age in years.",
        "example": "32 years",
    },
    "hospitalization_days": {
        "value": "",
        "required": True,
        "description": "The total number of days the Patient was admitted.",
        "example": "3 days",
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
        "description": "(Optional) The specific hospital department the patient was admitted to.",
        "example": "Cardiology",
    },
}
