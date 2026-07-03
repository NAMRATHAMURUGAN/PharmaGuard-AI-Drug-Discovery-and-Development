import pandas as pd

print("=" * 60)
print("DRUG MASTER CREATION")
print("=" * 60)

# -----------------------------
# Load Clean Dataset
# -----------------------------

df = pd.read_csv("datasets/ddinter_clean.csv")

# -----------------------------
# Collect Unique Drugs
# -----------------------------

drug_set = set(df["Drug_A"]).union(
    set(df["Drug_B"])
)

# -----------------------------
# Convert To DataFrame
# -----------------------------

drug_df = pd.DataFrame(
    sorted(list(drug_set)),
    columns=["Drug_Name"]
)

# -----------------------------
# Save
# -----------------------------

output_file = "datasets/drug_master.csv"

drug_df.to_csv(
    output_file,
    index=False
)

print(
    f"\nUnique Drugs: {len(drug_df)}"
)

print(
    f"Saved: {output_file}"
)

print("\nSample Drugs:")

print(drug_df.head())

print("\n[DONE]")