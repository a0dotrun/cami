from typing import Any

from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from .claim import Claim, BillItem
from .policy import DefaultPolicy
from .patient import Patient, PatientPolicy
from .engine import RuleEngine


def rule_engine_tool(claim: dict) -> dict:

    return
