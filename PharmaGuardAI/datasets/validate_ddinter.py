import pandas as pd

print("=" * 60)
print("DDINTER DATASET VALIDATION")
print("=" * 60)

# Load Dataset
df = pd.read_csv("datasets/ddinter_merged.csv")

print(f"\nTotal Records: {len(df):,}")
print(f"Total Columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())

# --------------------------------------------------
# Validation 1: Null Values
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 1: NULL VALUE CHECK")
print("=" * 60)

print(df.isnull().sum())

# --------------------------------------------------
# Validation 2: Unique Drugs in Drug_A
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 2: UNIQUE DRUGS IN DRUG_A")
print("=" * 60)

drug_a_unique = df["Drug_A"].nunique()

print(f"Unique Drug_A: {drug_a_unique:,}")

# --------------------------------------------------
# Validation 3: Unique Drugs in Drug_B
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 3: UNIQUE DRUGS IN DRUG_B")
print("=" * 60)

drug_b_unique = df["Drug_B"].nunique()

print(f"Unique Drug_B: {drug_b_unique:,}")

# --------------------------------------------------
# Validation 4: Combined Unique Drugs
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 4: COMBINED UNIQUE DRUGS")
print("=" * 60)

combined_drugs = set(df["Drug_A"]).union(set(df["Drug_B"]))

print(f"Total Unique Drugs: {len(combined_drugs):,}")

# --------------------------------------------------
# Validation 5: Unique DDInter IDs
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 5: UNIQUE DDINTER IDS")
print("=" * 60)

combined_ids = set(df["DDInterID_A"]).union(set(df["DDInterID_B"]))

print(f"Total Unique DDInter IDs: {len(combined_ids):,}")

# --------------------------------------------------
# Validation 6: Case Sensitivity Check
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 6: CASE NORMALIZATION CHECK")
print("=" * 60)

normalized_drugs = (
    pd.concat([df["Drug_A"], df["Drug_B"]])
    .astype(str)
    .str.strip()
    .str.lower()
    .unique()
)

print(
    f"Unique Drugs After Normalization: "
    f"{len(normalized_drugs):,}"
)

# --------------------------------------------------
# Validation 7: Severity Distribution
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 7: SEVERITY DISTRIBUTION")
print("=" * 60)

print(df["Level"].value_counts())

# --------------------------------------------------
# Validation 8: Duplicate Interaction Check
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 8: DUPLICATE INTERACTIONS")
print("=" * 60)

duplicates = df.duplicated(
    subset=["Drug_A", "Drug_B", "Level"]
).sum()

print(f"Duplicate Rows: {duplicates:,}")

# --------------------------------------------------
# Validation 9: Sample Drugs
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION 9: SAMPLE DRUGS")
print("=" * 60)

sample_drugs = sorted(list(combined_drugs))[:20]

for drug in sample_drugs:
    print(drug)

# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 60)
print("FINAL VALIDATION SUMMARY")
print("=" * 60)

print(f"Total Records              : {len(df):,}")
print(f"Unique Drug Names          : {len(combined_drugs):,}")
print(f"Unique DDInter IDs         : {len(combined_ids):,}")
print(f"Normalized Unique Drugs    : {len(normalized_drugs):,}")
print(f"Duplicate Interactions     : {duplicates:,}")

if len(combined_drugs) == len(combined_ids):
    print("\n✅ Drug count validation PASSED")
else:
    print("\n⚠ Drug count validation requires review")

print("\n[DONE] DDInter validation completed.")