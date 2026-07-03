import pandas as pd
import requests
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

    existing = pd.read_csv(OUTPUT_FILE)

    completed = set(existing["Drug_Name"])

    print(f"Resuming from {len(completed)} mapped drugs")

else:

    completed = set()

# -------------------------
# Mapping Loop
# -------------------------

for idx, row in drug_df.iterrows():

    drug = row["Drug_Name"]

    if drug in completed:
        continue

    search_name = (
        str(drug)
        .replace("(topical)", "")
        .replace("(ophthalmic)", "")
        .replace("(nasal)", "")
        .replace("(liposomal)", "")
        .replace("(liposome)", "")
        .replace("(lipid complex)", "")
        .replace("(cholesteryl sulfate)", "")
        .strip()
    )

    smiles = None

    try:

        url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
            f"compound/name/{search_name}/property/"
            "CanonicalSMILES/JSON"
        )

        response = requests.get(
            url,
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            smiles = (
                data["PropertyTable"]
                ["Properties"][0]
                ["ConnectivitySMILES"]
            )

    except Exception as e:

        print(
            f"ERROR -> {drug}: {e}"
        )

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

    time.sleep(0.05)

print("\n[DONE] Mapping Complete")