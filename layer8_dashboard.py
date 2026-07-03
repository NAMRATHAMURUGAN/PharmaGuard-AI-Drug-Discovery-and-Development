from flask import Flask, render_template, jsonify, request

import os
import csv
import base64
import pickle

from layer5_patient_risk import create_patient_profile
from layer7_readiness_score import generate_readiness_report

# SHAP explainability may not import reliably in all environments,
# so delay loading until the analysis request.
quick_shap_explain = None
SHAP_AVAILABLE = False
SHAP_IMPORT_ATTEMPTED = False

from src.ddi.alias_resolver import resolve_alias
from src.ddi.drug_search import (
    search_drugs,
    drug_exists
)

from src.ddi.dual_view_analysis import (
    dual_view_analysis
)

from src.ddi.molecule_visualizer import (
    molecule_image_base64
)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

DRUG_ALIASES = {
    "aspirin": "Acetylsalicylic acid",
    "paracetamol": "Acetaminophen",
    "tylenol": "Acetaminophen"
}

# ==================================================
# LOAD DRUG DATABASE
# ==================================================

try:
    with open("datasets/smiles_lookup.pkl", "rb") as f:
        loaded = pickle.load(f)

    SMILES_LOOKUP = {
        str(k).strip().lower(): v
        for k, v in loaded.items()
        if k is not None
    }

    print(f"[OK] Loaded {len(SMILES_LOOKUP)} drugs")

except Exception as e:

    print(f"[ERROR] Could not load smiles_lookup.pkl")
    print(e)

    SMILES_LOOKUP = {}


def load_toxicity_metrics():
    path = "datasets/model_summary.csv"

    if not os.path.exists(path):
        return {"labels": [], "average": {}}

    labels = []
    totals = {"Accuracy": 0.0, "F1 Score": 0.0, "ROC-AUC": 0.0}
    count = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            count += 1
            accuracy = float(row.get("Accuracy") or 0)
            f1 = float(row.get("F1 Score") or 0)
            auc = float(row.get("ROC-AUC") or 0)

            totals["Accuracy"] += accuracy
            totals["F1 Score"] += f1
            totals["ROC-AUC"] += auc

            labels.append({
                "label": row.get("Label", ""),
                "best_model": row.get("Best Model", ""),
                "accuracy": round(accuracy, 4),
                "f1": round(f1, 4),
                "auc": round(auc, 4)
            })

    average = {
        "Accuracy": round(totals["Accuracy"] / count, 4) if count else 0.0,
        "F1 Score": round(totals["F1 Score"] / count, 4) if count else 0.0,
        "ROC-AUC": round(totals["ROC-AUC"] / count, 4) if count else 0.0
    }

    return {"labels": labels, "average": average}


def load_ddi_metrics():
    path = "results/model_comparison.csv"
    models = []

    deployed_model = "Unknown"
    if os.path.exists("models/ddi_rf.pkl"):
        deployed_model = "RandomForest"
    elif os.path.exists("models/ddi_xgb.pkl"):
        deployed_model = "XGBoost"

    if not os.path.exists(path):
        return {"models": models, "deployed_model": deployed_model}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            models.append({
                "model": row.get("Model", ""),
                "accuracy": round(float(row.get("Accuracy") or 0), 4),
                "precision": round(float(row.get("Precision") or 0), 4),
                "recall": round(float(row.get("Recall") or 0), 4),
                "f1": round(float(row.get("F1_Score") or 0), 4),
                "remarks": row.get("Remarks", "")
            })

    return {"models": models, "deployed_model": deployed_model}


# OVERVIEW STATS
# ==================================================

@app.route("/api/overview")
def overview():

    return jsonify({
        "toxicity_models": 12,
        "ddi_records": 130422,
        "mapped_drugs": len(SMILES_LOOKUP),
        "prediction_models": 2
    })


# ==================================================
# DRUG SEARCH
# ==================================================

@app.route("/api/drug-search")
def drug_search_api():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    query = DRUG_ALIASES.get(
        query.lower(),
        query
    )

    results = search_drugs(query)

    return jsonify(results[:10])


# ==================================================
# CHECK DRUG EXISTS
# ==================================================

@app.route("/api/check-drug")
def check_drug():

    drug = request.args.get("drug", "").strip()

    drug = DRUG_ALIASES.get(
        drug.lower(),
        drug
    )

    drug = resolve_alias(drug)
    exists = SMILES_LOOKUP.get(str(drug).strip().lower()) is not None

    return jsonify({
        "drug": drug,
        "exists": exists
    })


# ==================================================
# GET SMILES
# ==================================================

@app.route("/api/get-smiles")
def get_smiles():

    drug = request.args.get("drug", "").strip()

    drug = resolve_alias(drug)
    drug = DRUG_ALIASES.get(
        drug.lower(),
        drug
    )

    smiles = SMILES_LOOKUP.get(
        str(drug).strip().lower()
    )

    return jsonify({
        "drug": drug,
        "smiles": smiles
    })


# ==================================================
# PLACEHOLDER
# ==================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "running",
        "dashboard": "PharmaGuard AI"
    })




# ==================================================
# ANALYZER
# ==================================================


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # ==================================================
        # RECEIVE INPUT
        # ==================================================

        data = request.get_json(silent=True)

        if data is None:
            data = request.form.to_dict()

        if not data:
            return jsonify({
                "error": "Missing JSON payload or form data"
            }), 400

        drug_name = resolve_alias(
            data.get("drug_name", "")
        )

        co_drug = resolve_alias(
            data.get("co_drug", "")
        )

        # ==================================================
        # PATIENT CONDITIONS
        # ==================================================

        conds = [
            c.strip()
            for c in str(data.get(
                "conditions", ""
            )).split(",")
            if c.strip()
        ]

        # ==================================================
        # BUILD PATIENT PROFILE
        # ==================================================

        patient = create_patient_profile(

            age=float(data.get("age", 0)),

            weight_kg=float(
                data.get("weight", 0)
            ),

            egfr=float(
                data.get("egfr", 0)
            ),

            alt=float(
                data.get("alt", 0)
            ),

            ast=float(
                data.get("ast", 0)
            ),

            gender=data.get(
                "gender",
                "male"
            ),

            conditions=conds
        )

        # ==================================================
        # ==================================================
        # DOSE / OVERDOSE INPUT (optional)
        dose_factor = 100.0
        try:
            dose_factor = float(data.get("dose_factor", 100.0))
        except Exception:
            dose_factor = 100.0

        dose_ratio = dose_factor / 100.0

        if dose_ratio >= 2.0:
            overdose_risk = "High"
        elif dose_ratio >= 1.2:
            overdose_risk = "Moderate"
        else:
            overdose_risk = "Low"

        # FULL PHARMAGUARD PIPELINE
        # ==================================================

        report = generate_readiness_report(

            smiles=data["smiles"],

            drug_name=drug_name,

            co_drug=co_drug,

            patient=patient
        )

        # DDI explanation (from predictor) and molecule images for visualization
        ddi_explanation = report.get("ddi", {})

        # Molecule images for drug and co-drug (if smiles available)
        drug_smiles = SMILES_LOOKUP.get(str(drug_name).strip()) if drug_name else None
        co_smiles = SMILES_LOOKUP.get(str(co_drug).strip()) if co_drug else None

        drug_molecule_image = molecule_image_base64(drug_smiles) if drug_smiles else None
        co_molecule_image = molecule_image_base64(co_smiles) if co_smiles else None

        # Build clinical message
        clinical_message = ""
        tox_info = report.get("full_report", {}).get("toxicity", {})
        tox_score = tox_info.get("score", 0)
        tox_details = tox_info.get("details", {})

        if tox_details.get('intrinsic_override'):
            clinical_message = (
                f"Intrinsic hazard: {tox_details.get('intrinsic_reason','')}. "
                "Avoid administration — inherently highly toxic."
            )
        elif overdose_risk == 'High' and tox_score <= 0.4:
            clinical_message = (
                "Safe when used at standard dosing; however, overdose (>=2x) "
                "substantially increases toxicity — avoid high dosing."
            )
        elif tox_score >= 0.6:
            clinical_message = (
                "High molecular toxicity detected — avoid or seek specialist review."
            )
        else:
            clinical_message = "Appears safe when used as directed; monitor per recommendations."

        # Append DDI note if major interaction
        ddi_level = ddi_explanation.get('level', '') if isinstance(ddi_explanation, dict) else ''
        if ddi_level == 'Major':
            clinical_message += " Co-administration shows MAJOR interaction — contraindicated."

        # ==================================================
        # SHAP EXPLAINABILITY
        # ==================================================

        shap_features = []

        global SHAP_IMPORT_ATTEMPTED, SHAP_AVAILABLE, quick_shap_explain

        if not SHAP_IMPORT_ATTEMPTED:
            try:
                from module3_shap_explainability import quick_shap_explain as _quick_shap_explain
                quick_shap_explain = _quick_shap_explain
                SHAP_AVAILABLE = True
            except Exception:
                SHAP_AVAILABLE = False
            finally:
                SHAP_IMPORT_ATTEMPTED = True

        if SHAP_AVAILABLE:
            try:
                shap_features = quick_shap_explain(
                    data["smiles"],
                    drug_name,
                    top_n=10
                )
            except Exception:
                shap_features = []

        # ==================================================
        # SHAP IMAGE
        # ==================================================

        shap_image = None

        img_path = (
            f"shap_plots/"
            f"{drug_name}_SR-ARE_shap.png"
        )

        if os.path.exists(img_path):

            with open(
                img_path,
                "rb"
            ) as f:

                shap_image = (
                    base64.b64encode(
                        f.read()
                    )
                    .decode("utf-8")
                )

        # ==================================================
        # DUAL VIEW ANALYSIS
        # ==================================================

        dual_view = dual_view_analysis(
            data["smiles"]
        )

        # ==================================================
        # MOLECULAR IMAGE
        # ==================================================

        molecule_image = (
            molecule_image_base64(
                data["smiles"]
            )
        )

        # ==================================================
        # FUSION LAYER OUTPUT
        # ==================================================

        fusion_data = {

            "toxicity":

                round(
                    report["full_report"]
                    ["toxicity"]
                    ["score"] * 100,
                    2
                ),

            "ddi":

                round(
                    report["full_report"]
                    ["ddi"]
                    ["score"] * 100,
                    2
                ),

            "structural":

                round(
                    report["full_report"]
                    ["structural"]
                    ["score"] * 100,
                    2
                ),

            "patient":

                round(
                    report["full_report"]
                    ["patient"]
                    ["vulnerability"]
                    ["vulnerability_score"],
                    2
                ),

            "unified":

                report["unified"],

            "readiness":

                report["readiness"]
                ["readiness_score"]
        }

        toxicity_metrics = load_toxicity_metrics()
        ddi_metrics = load_ddi_metrics()

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        return jsonify({

            # ---------------------------
            # BASIC INFO
            # ---------------------------

            "drug_name":
                drug_name,

            "co_drug":
                co_drug,

            # ---------------------------
            # READINESS
            # ---------------------------

            "readiness":
                report["readiness"],

            "unified_score":
                report["unified"],

            # ---------------------------
            # TOXICITY
            # ---------------------------

            "toxicity":

                round(
                    report["full_report"]
                    ["toxicity"]
                    ["score"] * 100,
                    2
                ),

            # ---------------------------
            # VULNERABILITY
            # ---------------------------

            "vulnerability":

                report["full_report"]
                ["patient"]
                ["vulnerability"]
                ["vulnerability_score"],

            # ---------------------------
            # DDI
            # ---------------------------

            "ddi_level":

                report["full_report"]
                ["ddi"]
                ["level"],

            "ddi_score":

                round(
                    report["full_report"]
                    ["ddi"]
                    ["score"] * 100,
                    2
                ),

            # ---------------------------
            # COMPONENTS
            # ---------------------------

            "components":

                report["full_report"]
                ["unified"]
                ["components"],

            "sub_scores":

                report["sub_scores"],

            # ---------------------------
            # DOSAGE
            # ---------------------------

            "dosage":
                report["dosage"],

            # ---------------------------
            # RECOMMENDATIONS
            # ---------------------------

            "recommendations":

                report[
                    "recommendations"
                ],

            # ---------------------------
            # SHAP
            # ---------------------------

            "shap_features":
                shap_features,

            "shap_image":
                shap_image,

            # ---------------------------
            # DUAL VIEW
            # ---------------------------

            "dual_view":
                dual_view,

            "molecule_image":
                molecule_image,

            # ---------------------------
            # FUSION
            # ---------------------------

            "fusion":
                fusion_data,

            # ---------------------------
            # METRICS
            # ---------------------------

            "toxicity_metrics":
                toxicity_metrics,

            "ddi_metrics":
                ddi_metrics
            ,
            # Per-label probabilities from Layer 4 (if available)
            "toxicity_details":
                report.get("full_report", {}).get("toxicity", {}).get("details", {}),
            # Overdose and clinical guidance
            "dose_ratio": round(dose_ratio, 2),
            "overdose_risk": overdose_risk,

            # Clinical message synthesized from toxicity, DDI and overdose
            "clinical_message": clinical_message,

            # Intrinsic toxicity reason (if any)
            "intrinsic_reason": report.get("full_report", {}).get("toxicity", {}).get("details", {}).get("intrinsic_reason"),

            # DDI explanation and molecule visuals
            "ddi_explanation": ddi_explanation,
            "drug_molecule_image": drug_molecule_image,
            "co_drug_molecule_image": co_molecule_image,
        })

    except Exception as e:

        import traceback

        return jsonify({

            "error": str(e),

            "trace":
                traceback.format_exc()

        }), 500





# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHARMAGUARD AI DASHBOARD")
    print("=" * 60)

    app.run(
        debug=True,
        port=5000
    )
