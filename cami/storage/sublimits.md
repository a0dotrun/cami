# 🧾 Claim-Level Sublimits

This document outlines common claim-level sublimits used in health insurance claim processing. These can be integrated into a rule engine to determine admissibility and deduction logic.

---

## 1. Room Rent
- **Type:** `daily_limit`
- **Limit:** `₹3,000`
- **Description:** Maximum allowable per day for standard room rent. If exceeded, proportionate deduction applies on associated costs (doctor, surgery, etc.).

---

## 2. ICU Rent
- **Type:** `daily_limit`
- **Limit:** `₹5,000`
- **Description:** Cap on ICU room rent per day. Charges above this are either excluded or proportionately deducted.

---

## 3. Ambulance Charges
- **Type:** `per_claim_limit`
- **Limit:** `₹2,000`
- **Description:** Maximum reimbursable ambulance fee per hospitalization event.

---

## 4. Nursing Charges
- **Type:** `daily_limit`
- **Limit:** `₹500`
- **Description:** Maximum allowed for nursing charges per day during hospital stay.

---

## 5. Pre-Hospitalization
- **Type:** `period_and_amount_limit`
- **Duration:** `30 days`
- **Amount Limit:** `₹5,000`
- **Description:** Covers expenses before admission like diagnostics, consultation, and medicines.

---

## 6. Post-Hospitalization
- **Type:** `period_and_amount_limit`
- **Duration:** `60 days`
- **Amount Limit:** `₹7,000`
- **Description:** Covers follow-up consultations, medicines, and tests after discharge.

---

## 7. Consultation Charges
- **Type:** `per_visit_limit`
- **Limit:** `₹1,000`
- **Description:** Maximum allowed per consultation during pre/post-hospitalization.

---

## 8. Diagnostics
- **Type:** `sub_category_limit`
- **Limit:** `₹15,000`
- **Description:** Cap on pathology, imaging, and diagnostic test charges.

---

## 9. Pharmacy
- **Type:** `category_limit`
- **Limit:** `₹20,000`
- **Description:** Limit for prescribed in-hospital medications and pharmacy expenses.

---

## 10. AYUSH Inpatient
- **Type:** `annual_limit`
- **Limit:** `₹50,000`
- **Description:** Cap on inpatient treatment under Ayurveda, Yoga, Unani, Siddha, and Homeopathy.

---

## 11. Hospital Registration Fees
- **Type:** `non_payable`
- **Payable:** `false`
- **Description:** Admission or registration charges are excluded from coverage.

---

## 12. Consumables
- **Type:** `non_payable`
- **Payable:** `false`
- **Description:** Non-medical consumables like gloves, syringes, hand sanitizers, cotton are not reimbursed.

---

## 13. Investigations Without Prescription
- **Type:** `non_payable`
- **Payable:** `false`
- **Description:** Diagnostics not backed by doctor’s prescription are inadmissible.

---

## 14. Food and Beverages
- **Type:** `non_payable`
- **Payable:** `false`
- **Description:** Charges for food for companions or unprescribed meals are excluded.

---

## 15. Hospital Cash Benefit *(Optional Rider)*
- **Type:** `fixed_daily_benefit`
- **Limit:** `₹1,000/day`
- **Description:** Fixed daily payout if rider is active; not linked to actual expenses.

---
