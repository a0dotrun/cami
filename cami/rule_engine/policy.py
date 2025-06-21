import json


class DefaultPolicy:
    def __init__(self):
        self.json_path = "./storage/default-policy.json"
        self.covered_procedures = []
        self._load_policy()

    def _load_policy(self):
        with open(self.json_path) as json_file:
            policy_definition = json.load(json_file)
            self.covered_procedures = policy_definition["covered_procedures"]

    def process_procedure_claim(self, procedure_code):
        for procedure in self.covered_procedures:
            if procedure["procedure_code"] == procedure_code:
                # If procedure is covered, pay the part
                return 1 - procedure.get("co_pay", 0)

        return 0  # If procedure is not covered, cannot be claimed
