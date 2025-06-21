from rule_engine import *


if __name__ == "__main__":
    import datetime

    claim = {
        "patient": patient,
        "hospital": "Jupiter Hospital and Institute of Vascular Surgery, No.28, 7th Main, 9th Cross, Malleswaram, Bangalore, 560003",
        "procedure": "Kidney Dialysis",
        "total_bills": 398300,
        "bill_items": [
            {"name": "Dialysis", "amount": 350000},
            {"name": "Injections", "amount": 6000},
            {"name": "Blood Work", "amount": 7800},
            {"name": "Kidney Tests", "amount": 34500},
        ]
    }

    print(RuleEngine(claim=claim).process())
