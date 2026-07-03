import pandas as pd

print("=" * 60)
print("DDINTER CLEANING PIPELINE")
print("=" * 60)

# -----------------------------
# Load Dataset
# -----------------------------

df = pd.read_csv("datasets/ddinter_merged.csv")

print(f"\nOriginal Shape: {df.shape}")

# -----------------------------
# Remove Unknown Severity
# -----------------------------

df = df[df["Level"] != "Unknown"]

print(f"\nAfter Removing Unknown: {df.shape}")

# -----------------------------
# Remove Duplicate Interactions
# -----------------------------

df = df.drop_duplicates(
    subset=["Drug_A", "Drug_B", "Level"]
)

print(f"\nAfter Removing Duplicates: {df.shape}")

# -----------------------------
# Reset Index
# -----------------------------

df = df.reset_index(drop=True)

# -----------------------------
# Save Clean Dataset
# -----------------------------

output_file = "datasets/ddinter_clean.csv"

df.to_csv(output_file, index=False)

print(f"\nSaved: {output_file}")

print("\nClass Distribution:")

print(df["Level"].value_counts())

print("\n[DONE] Cleaning Complete")