import dataclasses
import datetime
from pathlib import Path


@dataclasses.dataclass
class Policy:
    id: str
    name: str
    sum_insured: int
    effective_date: datetime.datetime


class CamiLitePolicy(Policy):
    id = "CAMI2025-Lite"
    name = "Cami Lite"
    sum_insured = 500000  # 5Lakhs
    effective_date = datetime.date(year=2025, month=6, day=1)

    @staticmethod
    def read():
        path = Path.cwd() / "../../storage/cami-lite.md"
        with open(path, "r") as f:
            return f.read()


class CamiProPolicy(Policy):
    id = "CAMI2025-Pro"
    name = "Cami Pro"
    sum_insured = 1000000  # 10Lakhs
    effective_date = datetime.date(year=2025, month=6, day=1)

    @staticmethod
    def read():
        path = Path.cwd() / "../../storage/cami-pro.md"
        with open(path, "r") as f:
            return f.read()


def get_policy_by_id(policy_id):
    return CamiLitePolicy if policy_id == CamiProPolicy.id else CamiProPolicy
