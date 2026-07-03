import pandas as pd

merged = pd.read_csv("datasets/ddinter_merged.csv")
clean = pd.read_csv("datasets/ddinter_clean.csv")

merged_drugs = set(merged["Drug_A"]).union(
    set(merged["Drug_B"])
)

clean_drugs = set(clean["Drug_A"]).union(
    set(clean["Drug_B"])
)

missing_drugs = merged_drugs - clean_drugs

print("=" * 60)
print("DRUG COUNT COMPARISON")
print("=" * 60)

print(f"Original Drugs : {len(merged_drugs)}")
print(f"Clean Drugs    : {len(clean_drugs)}")
print(f"Missing Drugs  : {len(missing_drugs)}")

print("\nMissing Drugs:")

for drug in sorted(missing_drugs):
    print(drug)