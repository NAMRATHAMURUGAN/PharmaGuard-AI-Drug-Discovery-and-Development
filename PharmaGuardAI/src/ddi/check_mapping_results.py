import pandas as pd

df = pd.read_csv(
    "datasets/drug_smiles_mapping.csv"
)

mapped = df["SMILES"].notna().sum()
failed = df["SMILES"].isna().sum()

print("Mapped :", mapped)
print("Failed :", failed)

print(
    "Coverage:",
    round(mapped/len(df)*100, 2),
    "%"
)