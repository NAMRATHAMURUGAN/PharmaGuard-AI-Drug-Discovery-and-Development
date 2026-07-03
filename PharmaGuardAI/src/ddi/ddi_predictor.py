import pickle
import joblib
import numpy as np

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator

from src.ddi.alias_resolver import resolve_alias


# --------------------------------------------------
# Load Assets Once
# --------------------------------------------------

with open("datasets/smiles_lookup.pkl", "rb") as f:
    SMILES_LOOKUP = pickle.load(f)

MODEL = joblib.load("models/ddi_rf.pkl")

MORGAN = GetMorganGenerator(
    radius=2,
    fpSize=1024
)

LABEL_MAP = {
    0: "Minor",
    1: "Moderate",
    2: "Major"
}

SEVERITY_SCORE = {
    "Minor": 0.2,
    "Moderate": 0.5,
    "Major": 1.0
}

# Load rule-based DDInter lookup (if available)
DDI_LOOKUP = {}
try:
    import pandas as pd
    df = pd.read_csv("datasets/ddinter_merged.csv")
    for _, row in df.iterrows():
        a = str(row.get("Drug_A", "")).strip().lower()
        b = str(row.get("Drug_B", "")).strip().lower()
        level = row.get("Level", "").strip()
        if a and b:
            DDI_LOOKUP[(a, b)] = dict(row)
            DDI_LOOKUP[(b, a)] = dict(row)
except Exception:
    # missing file is OK — fallback to model
    DDI_LOOKUP = {}


# --------------------------------------------------
# Molecular Features
# --------------------------------------------------

def molecular_features(smiles):

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return None

    descriptors = np.array([
        Descriptors.MolWt(mol),
        Descriptors.MolLogP(mol),
        rdMolDescriptors.CalcTPSA(mol),
        rdMolDescriptors.CalcNumHBA(mol),
        rdMolDescriptors.CalcNumHBD(mol)
    ])

    fp = MORGAN.GetFingerprint(mol)

    fp_array = np.array(list(fp))

    return np.concatenate(
        [descriptors, fp_array]
    )


# --------------------------------------------------
# DDI Prediction
# --------------------------------------------------

def predict_ddi(drug_a, drug_b):

    # -----------------------------------
    # Alias Resolution
    # -----------------------------------

    drug_a = resolve_alias(drug_a)
    drug_b = resolve_alias(drug_b)

    # -----------------------------------
    # Validation
    # -----------------------------------

    if drug_a not in SMILES_LOOKUP:
        return {
            "found": False,
            "level": "Drug A Not Found",
            "score": 0.0
        }

    if drug_b not in SMILES_LOOKUP:
        return {
            "found": False,
            "level": "Drug B Not Found",
            "score": 0.0
        }

    # Try rule-based lookup first (DDInter merged dataset)
    key = (str(drug_a).strip().lower(), str(drug_b).strip().lower())
    if key in DDI_LOOKUP:
        row = DDI_LOOKUP[key]
        level = row.get("Level", "Unknown")
        score = SEVERITY_SCORE.get(level, 0.0)
        return {
            "found": True,
            "drug_a": drug_a,
            "drug_b": drug_b,
            "level": level,
            "score": score,
            "method": "lookup",
            "rule_row": row,
            "lookup_method": "dataset"
        }
    # If not found in DDInter, try reverse order (some entries may be stored reversed)
    reverse_key = (str(drug_b).strip().lower(), str(drug_a).strip().lower())
    if reverse_key in DDI_LOOKUP:
        row = DDI_LOOKUP[reverse_key]
        level = row.get("Level", "Unknown")
        score = SEVERITY_SCORE.get(level, 0.0)
        return {
            "found": True,
            "drug_a": drug_a,
            "drug_b": drug_b,
            "level": level,
            "score": score,
            "method": "lookup",
            "rule_row": row,
            "lookup_method": "dataset_reversed"
        }

    feat_a = molecular_features(
        SMILES_LOOKUP[drug_a]
    )

    feat_b = molecular_features(
        SMILES_LOOKUP[drug_b]
    )

    fused = np.concatenate(
        [feat_a, feat_b]
    ).reshape(1, -1)

    # model prediction + probabilities
    pred = MODEL.predict(fused)[0]
    probs = None
    try:
        probs_arr = MODEL.predict_proba(fused)[0]
        probs = {
            LABEL_MAP[i]: float(probs_arr[i])
            for i in range(len(probs_arr))
        }
    except Exception:
        probs = None

    level = LABEL_MAP[int(pred)]

    # Basic feature summaries for transparency
    def desc_summary(smiles):
        m = Chem.MolFromSmiles(smiles)
        if m is None:
            return {}
        return {
            "MolWt": round(Descriptors.MolWt(m), 2),
            "LogP": round(Descriptors.MolLogP(m), 2),
            "TPSA": round(rdMolDescriptors.CalcTPSA(m), 2),
            "HBA": int(rdMolDescriptors.CalcNumHBA(m)),
            "HBD": int(rdMolDescriptors.CalcNumHBD(m))
        }

    return {
        "found": True,
        "drug_a": drug_a,
        "drug_b": drug_b,
        "level": level,
        "score": SEVERITY_SCORE[level],
        "method": "model",
        "class_probabilities": probs,
        "features": {
            "drug_a": desc_summary(SMILES_LOOKUP[drug_a]),
            "drug_b": desc_summary(SMILES_LOOKUP[drug_b])
        }
    }




    