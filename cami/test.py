from rule_engine import *


if __name__ == "__main__":
    import datetime

    patient = Patient(name="Kireeti", age=31, gender="M", policy=PatientPolicy())
    bill_items = [
        BillItem(procedure="Cancer Treatment", amount=350000),
        BillItem(procedure="PROC_UTERINE_EMBO", amount=67000)
    ]
    claim = Claim(
        patient=patient,
        hospital="Apollo Bangalore",
        date=datetime.datetime.now(),
        policy=DefaultPolicy(),
        bill_items=bill_items
    )

    print(RuleEngine(claim=claim).process())
