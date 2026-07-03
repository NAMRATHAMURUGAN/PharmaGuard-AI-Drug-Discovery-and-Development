import pandas as pd
import pubchempy as pcp
import time
import os

INPUT_FILE = "datasets/drug_master.csv"
OUTPUT_FILE = "datasets/drug_smiles_mapping.csv"

# -------------------------
# Load Drug Master
# -------------------------

drug_df = pd.read_csv(INPUT_FILE)

# -------------------------
# Resume Support
# -------------------------

if os.path.exists(OUTPUT_FILE):

    mapped_df = pd.read_csv(OUTPUT_FILE)

    completed = set(mapped_df["Drug_Name"])

    print(f"Resuming... {len(completed)} drugs already mapped")

else:

    mapped_df = pd.DataFrame(
        columns=["Drug_Name", "SMILES"]
    )

    completed = set()

# -------------------------
# Mapping Loop
# -------------------------

for idx, row in drug_df.iterrows():

    drug = row["Drug_Name"]

    if drug in completed:
        continue

    search_name = drug

    # remove formulation tags

    search_name = (
        search_name
        .replace("(topical)", "")
        .replace("(ophthalmic)", "")
        .replace("(nasal)", "")
        .replace("(liposomal)", "")
        .replace("(liposome)", "")
        .strip()
    )

    try:

        compounds = pcp.get_compounds(
            search_name,
            "name"
        )

        if len(compounds) > 0:

            smiles = compounds[0].canonical_smiles

        else:

            smiles = None

    except Exception:

        smiles = None

    pd.DataFrame(
        [[drug, smiles]],
        columns=["Drug_Name", "SMILES"]
    ).to_csv(
        OUTPUT_FILE,
        mode="a",
        header=not os.path.exists(OUTPUT_FILE),
        index=False
    )

    print(
        f"[{idx+1}/{len(drug_df)}] "
        f"{drug} -> "
        f"{'FOUND' if smiles else 'NOT FOUND'}"
    )

    time.sleep(0.1)

print("\n[DONE] Drug Mapping Complete")