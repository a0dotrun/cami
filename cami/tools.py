def claim_status() -> str:
    """Retrieves the current status of the insurance claim.

    Args:
        policy_number (str): The policy number of the insurance claim.

    Returns:
        dict: A dictionary containing the claim information.
        Includes a 'status' key ('sucess' or 'error').
        If 'success', includes 'claim_status' key with claim details.
        If 'error', includes 'error_message' key.
    """
    return {
        "status": "sucess",
        "claim_status": (
            "Your claim is currently under review. "
            "We will notify you once a decision has been made."
        ),
    }
