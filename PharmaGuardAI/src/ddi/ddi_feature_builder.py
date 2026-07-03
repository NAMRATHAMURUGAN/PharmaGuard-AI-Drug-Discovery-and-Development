import pandas as pd
import numpy as np
import pickle
import os
import warnings

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator

warnings.filterwarnings("ignore")

print("=" * 70)
print("PHARMAGUARD AI - DDI FEATURE GENERATION")
print("=" * 70)

# ==========================================================
# CONFIGURATION
# ==========================================================

DDI_FILE = "datasets/ddinter_clean.csv"
LOOKUP_FILE = "datasets/smiles_lookup.pkl"

FEATURES_FILE = "datasets/ddi_features.npy"
LABELS_FILE = "datasets/ddi_labels.npy"

CHECKPOINT_DIR = "datasets/checkpoints"

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("\nLoading DDInter dataset...")

df = pd.read_csv(DDI_FILE)

print(f"Interactions Loaded: {len(df):,}")

print("\nLoading SMILES lookup...")

with open(LOOKUP_FILE, "rb") as f:
    smiles_lookup = pickle.load(f)

print(f"Mapped Drugs Available: {len(smiles_lookup):,}")

# ==========================================================
# LABEL ENCODING
# ==========================================================

label_map = {
    "Minor": 0,
    "Moderate": 1,
    "Major": 2
}

# ==========================================================
# MORGAN GENERATOR
# ==========================================================

morgan_generator = GetMorganGenerator(
    radius=2,
    fpSize=1024
)

# ==========================================================
# FEATURE FUNCTION
# ==========================================================

def get_molecular_features(smiles):

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return None

    descriptors = np.array([

        Descriptors.MolWt(mol),

        Descriptors.MolLogP(mol),

        rdMolDescriptors.CalcTPSA(mol),

        rdMolDescriptors.CalcNumHBA(mol),

        rdMolDescriptors.CalcNumHBD(mol)

    ], dtype=np.float32)

    fp = morgan_generator.GetFingerprint(mol)

    fingerprint = np.array(
        list(fp),
        dtype=np.float32
    )

    features = np.concatenate(
        [
            descriptors,
            fingerprint
        ]
    )

    return features

# ==========================================================
# DATASET BUILDING
# ==========================================================

print("\nGenerating DDI feature matrix...")

X = []
y = []

processed = 0
skipped = 0

for idx, row in df.iterrows():

    drug_a = row["Drug_A"]
    drug_b = row["Drug_B"]

    if (
        drug_a not in smiles_lookup
        or
        drug_b not in smiles_lookup
    ):
        skipped += 1
        continue

    try:

        smiles_a = smiles_lookup[drug_a]
        smiles_b = smiles_lookup[drug_b]

        feat_a = get_molecular_features(smiles_a)
        feat_b = get_molecular_features(smiles_b)

        if feat_a is None or feat_b is None:

            skipped += 1
            continue

        fused_features = np.concatenate(
            [
                feat_a,
                feat_b
            ]
        )

        X.append(fused_features)

        y.append(
            label_map[row["Level"]]
        )

        processed += 1

        # =====================================
        # CHECKPOINT EVERY 5000 SAMPLES
        # =====================================

        if processed % 5000 == 0:

            print(
                f"[Checkpoint] "
                f"Processed: {processed:,} | "
                f"Skipped: {skipped:,}"
            )

            np.save(
                os.path.join(
                    CHECKPOINT_DIR,
                    f"features_{processed}.npy"
                ),
                np.array(X, dtype=np.float32)
            )

            np.save(
                os.path.join(
                    CHECKPOINT_DIR,
                    f"labels_{processed}.npy"
                ),
                np.array(y)
            )

    except Exception as e:

        skipped += 1

        continue

# ==========================================================
# FINAL SAVE
# ==========================================================

print("\nConverting to NumPy arrays...")

X = np.array(
    X,
    dtype=np.float32
)

y = np.array(y)

print("\nDataset Summary")
print("-" * 40)

print(f"Feature Matrix Shape : {X.shape}")
print(f"Labels Shape         : {y.shape}")

print(f"Processed Samples    : {processed:,}")
print(f"Skipped Samples      : {skipped:,}")

print(
    f"\nFeature Dimension    : "
    f"{X.shape[1]}"
)

# ==========================================================
# SAVE FINAL DATASET
# ==========================================================

print("\nSaving final dataset...")

np.save(
    FEATURES_FILE,
    X
)

np.save(
    LABELS_FILE,
    y
)

print("\nSaved Files:")

print(FEATURES_FILE)
print(LABELS_FILE)

print("\n[DONE] DDI Feature Generation Completed")