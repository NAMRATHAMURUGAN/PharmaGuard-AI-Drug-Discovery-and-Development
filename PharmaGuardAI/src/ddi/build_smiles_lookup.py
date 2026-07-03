import pandas as pd
import pickle

print("=" * 60)
print("BUILDING SMILES LOOKUP")
print("=" * 60)

# -----------------------------
# Load Mapping File
# -----------------------------

df = pd.read_csv(
    "datasets/drug_smiles_mapping.csv"
)

# Remove failed mappings

df = df.dropna(subset=["SMILES"])

print(f"\nMapped Drugs: {len(df)}")

# -----------------------------
# Build Dictionary
# -----------------------------

smiles_lookup = dict(
    zip(
        df["Drug_Name"],
        df["SMILES"]
    )
)

# -----------------------------
# Save Lookup
# -----------------------------

with open(
    "datasets/smiles_lookup.pkl",
    "wb"
) as f:

    pickle.dump(
        smiles_lookup,
        f
    )

print(
    "\nSaved: datasets/smiles_lookup.pkl"
)

print(
    f"Dictionary Size: {len(smiles_lookup)}"
)

print("\n[DONE]")