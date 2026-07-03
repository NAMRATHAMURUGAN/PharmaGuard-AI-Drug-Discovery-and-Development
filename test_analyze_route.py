from layer5_patient_risk import create_patient_profile
from layer7_readiness_score import generate_readiness_report

patient = create_patient_profile(
    age=45,
    weight_kg=70,
    egfr=80,
    alt=30,
    ast=25
)

report = generate_readiness_report(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    drug_name="Aspirin",
    co_drug="Warfarin",
    patient=patient
)

print(report["readiness"])
print(report["sub_scores"])
print(report["dosage"])
print(report["recommendations"])