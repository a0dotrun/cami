from typing import Any

import restate

from cami.utils.types import ClaimHistory


class AskForApproval:
    """
    Request approval for a reimbursement from the designated approver.

    Args:
        amount (float): The amount requested.
        purpose (str): The reason for the reimbursement.

    Returns:
        A dictionary containing the approval status and metadata:
            status (str): The current status (e.g., "pending").
            approver (str): The name of the approver handling the request.
            message (str): A human-readable message about the request status.
    """

    name = "ask_for_approval"

    def __init__(
        self,
        ctx: restate.ObjectContext,
    ):
        self.ctx = ctx

    async def __call__(self, amount: float, purpose: str) -> dict[str, Any]:
        print("-> [In Tool] ctx.key():", self.ctx.key())
        print("-> [In Tool] args:", amount, purpose)
        return {
            "status": "pending",
            "approver": "Sean Zhou",
            "message": "Your request is being processed. Please wait.",
        }

    @property
    def __name__(self):
        return self.name


class GetClaimStatus:
    """
    Returms claim approval status for a reimbursement from the designated approver.

    Returns:
        A dictionary containing the approval status and metadata:
            status (str): The current status (e.g., "success").
            claims (list): List of claims with keys: purpose, amount, status
    """

    name = "get_approval_status"

    def __init__(
        self,
        ctx: restate.ObjectContext,
    ):
        self.ctx = ctx

    async def __call__(
        self,
    ) -> dict[str, Any]:
        claims = await self.ctx.get("claims", type_hint=ClaimHistory) or ClaimHistory()

        return {
            "status": "success",
            "claims": claims,
        }

    @property
    def __name__(self):
        return self.name
