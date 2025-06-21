STAR_HEALTH_LITE = """
# Star Health Lite - Policy Coverage Summary

## Covered Treatments

| Treatment                        | Description                                               | Coverage Amount (₹)  |
|----------------------------------|-----------------------------------------------------------|----------------------|
| **Dengue Fever Treatment**       | Hospitalization and medication for vector-borne fever     | ₹50,000              |
| **Typhoid Treatment**            | In-patient care for bacterial typhoid infection           | ₹40,000              |
| **Appendicitis Surgery**         | Laparoscopic or open appendectomy                         | ₹1,00,000            |
| **Fracture Treatment**           | Emergency care and surgery for bone fractures             | ₹75,000              |
| **Gallbladder Surgery**          | Removal of gallbladder due to stones or infection         | ₹90,000              |
| **Pneumonia Hospitalization**    | In-patient treatment for severe respiratory infection     | ₹60,000              |
| **Diabetes Complication Care**   | Treatment for hypoglycemia, DKA, and other complications  | ₹70,000              |
| **Heart Attack Stabilization**   | Initial treatment and monitoring in ICU                   | ₹1,50,000            |
| **Kidney Stone Removal**         | Non-invasive or surgical removal of kidney stones         | ₹80,000              |
| **COVID-19 Treatment**           | Hospitalization for symptomatic COVID-19 cases            | ₹1,00,000            |
"""


STAR_HEALTH_PRO = """
# Star Health Pro - Policy Coverage Summary

## Covered Treatments

| Treatment                          | Description                                                    | Coverage Amount (₹)  |
|------------------------------------|----------------------------------------------------------------|----------------------|
| **Cancer Treatment (All Stages)**  | Chemotherapy, radiation, surgery, and follow-up care           | ₹5,00,000            |
| **Cardiac Surgery (CABG, Valve)**  | Advanced heart procedures including bypass and valve repair    | ₹4,00,000            |
| **Chronic Kidney Disease Dialysis**| Dialysis sessions and supportive medication                    | ₹3,00,000            |
| **Liver Cirrhosis Management**     | In-patient and long-term treatment for liver failure           | ₹2,50,000            |
| **Orthopedic Surgeries**           | Knee replacement, hip surgery, and complex fractures           | ₹2,00,000            |
| **Neurological Disorders Care**    | Stroke, epilepsy, and neurodegenerative disease management     | ₹2,50,000            |
| **Maternity & Newborn Care**       | Delivery (C-section/normal) and neonatal ICU                   | ₹1,50,000            |
| **Mental Health In-patient Care**  | Hospitalization for psychiatric treatment                      | ₹1,00,000            |
| **Diabetes & Hypertension Package**| Continuous care for Type I/II and BP management                | ₹1,50,000            |
| **Accident & Trauma Care**         | Emergency treatment and surgery for major accidents            | ₹3,00,000            |
"""


def get_doc_from_policy(policy_id: str) -> str:
    docs = {
        "SHL7760": STAR_HEALTH_LITE,
        "SHS1234": STAR_HEALTH_PRO,
    }
    doc = docs.get(policy_id)
    if doc is None:
        return "No document found for the given policy ID."
    return doc
