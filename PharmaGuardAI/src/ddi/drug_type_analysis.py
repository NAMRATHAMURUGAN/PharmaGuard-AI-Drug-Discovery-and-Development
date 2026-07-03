import pandas as pd

df = pd.read_csv("datasets/drug_master.csv")

keywords = [
    "vaccine",
    "immunoglobulin",
    "factor",
    "human",
    "recombinant",
    "pegol",
    "alfa",
    "beta",
    "protein",
    "antibody",
]

biologics = []

for drug in df["Drug_Name"]:

    name = str(drug).lower()

    if any(k in name for k in keywords):
        biologics.append(drug)

print("\nPotential Biologics/Proteins:")

for drug in biologics:
    print(drug)

print("\nCount:", len(biologics))

print(
    "\nEstimated Small Molecules:",
    len(df) - len(biologics)
)