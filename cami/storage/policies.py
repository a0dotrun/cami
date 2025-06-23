from pathlib import Path


def get_doc_from_policy(policy_id: str) -> str:
    CAMI_LITE_POLICY = ""
    CAMI_PRO_POLICY = ""

    with open(Path.cwd() / "cami/storage/cami-lite.md") as file:
        CAMI_LITE_POLICY = file.read()

    with open(Path.cwd() / "cami/storage/cami-pro.md") as file:
        CAMI_PRO_POLICY = file.read()

    docs = {
        "CAMI2025-Lite": CAMI_LITE_POLICY,
        "CAMI2025-Pro": CAMI_PRO_POLICY,
    }
    doc = docs.get(policy_id)
    if doc is None:
        return "No document found for the given policy ID."
    return doc
