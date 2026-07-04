# PharmaGuard AI — Drug Discovery & Development Platform

An 8-layer machine learning pipeline for early-stage drug safety assessment — combining molecular toxicity prediction, drug-drug interaction (DDI) analysis, patient-aware risk scoring, and explainable AI, wrapped in an interactive dashboard.

## Overview

PharmaGuard AI takes a drug (by name or SMILES string) and runs it through a layered pipeline that predicts toxicity risk, checks for interactions with other drugs, factors in patient-specific risk, and produces a single interpretable "readiness score" — with a visual breakdown of *why* the model made that call.

## Pipeline Architecture

| Layer | Module | Purpose |
|---|---|---|
| 1–2 | `layer1_2_preprocessing.py` | Fetches SMILES strings, validates molecules, prepares raw input |
| 3 | `layer3_dual_view.py` | Generates dual molecular representations — RDKit descriptors + Morgan fingerprints |
| 4 | `layer4_toxicity_model.py` | Predicts toxicity across 12 Tox21 endpoints using Random Forest and XGBoost, with automatic best-model selection by ROC-AUC |
| 5 | `layer5_patient_risk.py` | Adds patient-specific risk factors on top of molecular toxicity |
| 6 | `layer6_risk_fusion.py` | Fuses molecular + patient + interaction risk into a unified score |
| 7 | `layer7_readiness_score.py` | Converts fused risk into a single, interpretable readiness score |
| 8 | `layer8_dashboard.py` | Serves results through an interactive dashboard |

**Explainability:** `module3_shap_explainability.py` uses SHAP to show which molecular features drove each prediction, so results aren't a black box.

**Drug-Drug Interaction (DDI):** Dedicated modules (`test_ddi_model.py`, `test_ddi_distribution.py`) check for interaction risk between drug pairs using DrugBank data.

**Drug lookup & search:** `check_drugbank.py`, `check_tox21.py`, `fetch_smiles.py`, and `DRUG_SYNONYMS_MAPPING.md` handle resolving drug names/synonyms to standardized identifiers and pulling reference data.

## Tech Stack

- **ML/Data:** Python, RDKit, Scikit-learn, XGBoost, SHAP
- **Backend/API:** FastAPI
- **Frontend:** HTML, CSS, JavaScript (dashboard in `PharmaGuardAI/`)
- **Datasets:** Tox21 (toxicity), DrugBank (drug interactions & metadata)

## Project Structure

```
PharmaGuard-AI-Drug-Discovery-and-Development/
├── PharmaGuardAI/                    # Frontend dashboard (HTML/CSS/JS)
├── layer1_2_preprocessing.py
├── layer3_dual_view.py
├── layer4_toxicity_model.py
├── layer5_patient_risk.py
├── layer6_risk_fusion.py
├── layer7_readiness_score.py
├── layer8_dashboard.py
├── module3_shap_explainability.py
├── fetch_smiles.py
├── check_drugbank.py
├── check_tox21.py
├── check_aspirin.py
├── DRUG_SYNONYMS_MAPPING.md
├── test_*.py                          # API, DDI, and dashboard test scripts
└── requirements.txt
```

## Setup & Usage

```bash
# Clone the repo
git clone https://github.com/NAMRATHAMURUGAN/PharmaGuard-AI-Drug-Discovery-and-Development.git
cd PharmaGuard-AI-Drug-Discovery-and-Development

# Install dependencies
pip install -r requirements.txt

# Run the preprocessing + model pipeline
python layer1_2_preprocessing.py

# Launch the dashboard
python layer8_dashboard.py
```

> Update this section with your actual entry point/run order if it differs.

## Future Scope

- Expand DDI coverage to a larger drug-pair dataset
- Add batch prediction support for high-throughput screening
- Deploy the dashboard for public/demo access

## Author

**Namratha Murugan** — [GitHub](https://github.com/NAMRATHAMURUGAN) · [LinkedIn](https://www.linkedin.com/in/namratha-murugan-7033ba295)
