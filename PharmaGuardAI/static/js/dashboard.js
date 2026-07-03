// =====================================================
// SIDEBAR NAVIGATION
// =====================================================

function showSection(id, el)
{
    document
    .querySelectorAll(".section")
    .forEach(section =>
    {
        section.classList.add("hidden");
    });

    document
    .getElementById(id)
    .classList.remove("hidden");

    document
    .querySelectorAll(".menu li")
    .forEach(item =>
    {
        item.classList.remove("active");
    });

    if(el)
    {
        el.classList.add("active");
    }
}


// =====================================================
// ADVANCED CLINICAL PARAMETERS
// =====================================================

function toggleClinical()
{
    const div =
        document.getElementById(
            "clinicalSection"
        );

    if(div.style.display === "none")
    {
        div.style.display = "block";
    }
    else
    {
        div.style.display = "none";
    }
}


// =====================================================
// DRUG SEARCH
// =====================================================

async function searchDrug(
    inputId,
    suggestionId
)
{
    const query =
        document
        .getElementById(inputId)
        .value
        .trim();

    const suggestionsDiv =
        document
        .getElementById(
            suggestionId
        );

    if(query.length < 2)
    {
        suggestionsDiv.innerHTML = "";
        return;
    }

    try
    {
        const response =
            await fetch(
                `/api/drug-search?q=${encodeURIComponent(query)}`
            );

        const drugs =
            await response.json();

        let html = "";

        drugs.forEach(drug =>
        {
            html +=
            `
            <div
                class="suggestion-item"
                onclick="
                    selectDrug(
                        '${drug}',
                        '${inputId}',
                        '${suggestionId}'
                    )
                "
            >
                ${drug}
            </div>
            `;
        });

        suggestionsDiv.innerHTML =
            html;
    }
    catch(error)
    {
        console.error(error);
    }
}


// =====================================================
// SELECT DRUG
// =====================================================

async function selectDrug(
    drug,
    inputId,
    suggestionId
)
{
    console.log("Selected:", drug);

    document
    .getElementById(inputId)
    .value = drug;

    document
    .getElementById(suggestionId)
    .innerHTML = "";

    // Only autofill SMILES
    if(inputId === "drug_name")
    {
        await loadSmiles(drug);
    }
}


// =====================================================
// AUTO LOAD SMILES
// =====================================================

async function loadSmiles(drug)
{
    try
    {
        const response =
            await fetch(
                `/api/get-smiles?drug=${encodeURIComponent(drug)}`
            );

        const data =
            await response.json();

        console.log("SMILES API:", data);

        const smilesInput =
            document.getElementById(
                "smiles"
            );

        if(data.smiles)
        {
            smilesInput.value =
                data.smiles;
        }
        else
        {
            smilesInput.value =
                "SMILES not found";
        }
    }
    catch(error)
    {
        console.error(error);

        document
        .getElementById("smiles")
        .value =
        "Error loading SMILES";
    }
}


// =====================================================
// ANALYZE
// =====================================================

async function runAnalysis()
{
    try
    {
        const payload =
        {
            drug_name:
                document
                .getElementById("drug_name")
                .value,

            smiles:
                document
                .getElementById("smiles")
                .value,

            co_drug:
                document
                .getElementById("co_drug")
                .value,

            age:
                parseFloat(
                    document
                    .getElementById("age")
                    .value
                ),

            weight:
                parseFloat(
                    document
                    .getElementById("weight")
                    .value
                ),

            egfr:
                parseFloat(
                    document
                    .getElementById("egfr")
                    .value
                ),

            alt:
                parseFloat(
                    document
                    .getElementById("alt")
                    .value
                ),

            ast:
                parseFloat(
                    document
                    .getElementById("ast")
                    .value
                ),

            gender:
                document
                .getElementById("gender")
                .value,

            conditions:
                document
                .getElementById("conditions")
                .value
        };

        document
            .getElementById("loadingStatus")
            .textContent = "Analyzing Toxicity...";

        document
            .getElementById("loadingOverlay")
            .style.display = "flex";

        const response =
            await fetch(
                "/analyze",
                {
                    method:"POST",

                    headers:
                    {
                        "Content-Type":
                        "application/json"
                    },

                    body:
                    JSON.stringify(payload)
                }
            );

        document
            .getElementById("loadingStatus")
            .textContent = "Checking Drug Interactions...";

        const data =
            await response.json();

        console.log(data);

        if(data.error)
        {
            document
                .getElementById("loadingOverlay")
                .style.display = "none";

            alert(
                "Backend Error:\n\n" +
                data.error
            );
            return;
        }

        document
            .getElementById("loadingStatus")
            .textContent = "Running Fusion Engine...";

        updateToxicity(data);

        updateDDI(data);

        updateMolecular(data);

        updateFusion(data);

        document
            .getElementById("loadingStatus")
            .textContent = "Generating SHAP...";

        updateSHAP(data);

        updateRecommendations(data);

        showSection('toxicity', document.querySelector('.menu li:nth-child(2)'));

        document
            .getElementById("loadingOverlay")
            .style.display = "none";
    }
    catch(error)
    {
        document
.getElementById("loadingOverlay")
.style.display = "none";
        console.error(error);

        alert(
            "Analysis Failed"
        );
    }
}


// =====================================================
// TOXICITY TAB
// =====================================================

// =====================================================
// TOXICITY TAB
// =====================================================

function updateToxicity(data)
{
    const div =
        document.getElementById(
            "toxicity_result"
        );

    if(!div) return;

    const toxicity = Number(data.toxicity);
    const isValid = Number.isFinite(toxicity);

    let badgeClass = "risk-low";
    let label = "LOW";
    let displayValue = "n/a";

    if(isValid)
    {
        displayValue = `${toxicity}%`;

        if(toxicity > 60)
        {
            badgeClass = "risk-high";
            label = "HIGH";
        }
        else if(toxicity > 30)
        {
            badgeClass = "risk-medium";
            label = "MODERATE";
        }
    }

    div.innerHTML =
    `
    <div class="${badgeClass}">
        ${label} TOXICITY
    </div>

    <br>

    <div class="result-value">
        ${displayValue}
    </div>

    <br>

    <p>
        Drug:
        <b>${data.drug_name || "Unknown"}</b>
    </p>
    `;

    renderToxicityMetrics(data.toxicity_metrics);

    // Render per-label probabilities if provided by backend
    if(data.toxicity_details && Object.keys(data.toxicity_details).length > 0)
    {
        const labelsHtml = Object.entries(data.toxicity_details).map(([label, val]) => {
            const pct = (Number(val) * 100).toFixed(2);
            return `<li><strong>${label}</strong>: ${pct}%</li>`;
        }).join("");

        div.innerHTML += `
            <div class="tox-label-probs">
                <h4>Per-label probabilities</h4>
                <ul>
                    ${labelsHtml}
                </ul>
            </div>
        `;
    }

    // Clinical guidance and overdose info
    if(data.clinical_message)
    {
        div.innerHTML += `
            <div class="clinical-message">
                <h4>Clinical Guidance</h4>
                <p>${data.clinical_message}</p>
                <p><strong>Dose factor:</strong> ${data.dose_ratio}x of standard — <em>${data.overdose_risk} overdose risk</em></p>
            </div>
        `;
    }
}


// =====================================================
// DDI TAB
// =====================================================

function updateDDI(data)
{
    const div =
        document
        .getElementById(
            "ddi_result"
        );

    if(!div) return;

    const severity = data.ddi_level || "Minor";
    let badgeClass = "badge-low";

    if(severity === "Moderate")
    {
        badgeClass = "badge-medium";
    }
    else if(severity === "Major" || severity === "Severe")
    {
        badgeClass = "badge-high";
    }

    div.innerHTML =
    `
    <div class="ddi-visual-card">
        <div class="ddi-flow">
            <div class="ddi-box">${data.drug_name || "Drug A"}</div>
            <div class="ddi-line"></div>
            <div class="ddi-box">${data.co_drug || "Drug B"}</div>
        </div>

        <div class="ddi-status-card">
            <div class="badge ${badgeClass}">
                ${badgeClass === 'badge-low' ? '🟢 MINOR' : badgeClass === 'badge-medium' ? '🟠 MODERATE' : '🔴 SEVERE'}
            </div>
            <h3>Interaction</h3>
            <p>Severity: <strong>${severity}</strong></p>
            <p>Score: <strong>${data.ddi_score != null ? data.ddi_score + "%" : "n/a"}</strong></p>
        </div>
    </div>
    `;

    renderDDIMetrics(data.ddi_metrics);

    // Render DDI explanation details if present
    if(data.ddi_explanation)
    {
        const det = data.ddi_explanation;
        let extra = '<div class="ddi-explanation"><h4>DDI Explanation</h4>';

        if(det.method === 'lookup' && det.rule_row)
        {
            extra += `<p><strong>Method:</strong> Dataset lookup</p>`;
            extra += `<p><strong>Rule:</strong> ${det.rule_row.Level || ''} — ${det.rule_row.Remarks || ''}</p>`;
        }
        else if(det.method === 'model')
        {
            extra += `<p><strong>Method:</strong> ML model</p>`;
            if(det.class_probabilities)
            {
                extra += `<div class="ddi-probs">`;
                Object.entries(det.class_probabilities).forEach(([k,v]) => {
                    const pct = (Number(v) * 100).toFixed(1);
                    extra += `<div class="prob-row"><span class="prob-label">${k}</span> <span class="prob-value">${pct}%</span></div>`;
                });
                extra += `</div>`;
            }
        }

        // feature summaries
        if(det.features)
        {
            extra += `<h5>Feature summary</h5>`;
            extra += `<div class="ddi-features"><div><strong>${data.drug_name}</strong>`;
            Object.entries(det.features.drug_a || {}).forEach(([k,v]) => {
                extra += `<p>${k}: ${v}</p>`;
            });
            extra += `</div><div><strong>${data.co_drug}</strong>`;
            Object.entries(det.features.drug_b || {}).forEach(([k,v]) => {
                extra += `<p>${k}: ${v}</p>`;
            });
            extra += `</div></div>`;
        }

        // Molecule images
        if(data.drug_molecule_image || data.co_drug_molecule_image)
        {
            extra += `<div class="ddi-mols">`;
            if(data.drug_molecule_image)
                extra += `<div class="mol"><img src="data:image/png;base64,${data.drug_molecule_image}" alt="drug"></div>`;
            if(data.co_drug_molecule_image)
                extra += `<div class="mol"><img src="data:image/png;base64,${data.co_drug_molecule_image}" alt="co-drug"></div>`;
            extra += `</div>`;
        }

        extra += '</div>';

        div.innerHTML += extra;
    }
}


// =====================================================
// MODEL METRICS

function renderDDIMetrics(metrics)
{
    const div = document.getElementById("ddi_metrics");

    if(!div)
    {
        return;
    }

    if(!metrics || !Array.isArray(metrics.models) || metrics.models.length === 0)
    {
        div.innerHTML =
        `<p>No DDI evaluation metrics available.</p>`;
        return;
    }

    let html =
    `
    <div class="metrics-card">
        <h3>DDI Model Evaluation</h3>
        <p><strong>Deployed Model:</strong> ${metrics.deployed_model}</p>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Model</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1</th>
                </tr>
            </thead>
            <tbody>
                ${metrics.models.map(model =>
                    `
                    <tr>
                        <td>${model.model}</td>
                        <td>${model.accuracy}</td>
                        <td>${model.precision}</td>
                        <td>${model.recall}</td>
                        <td>${model.f1}</td>
                    </tr>
                    `
                ).join("")}
            </tbody>
        </table>
    </div>
    `;

    div.innerHTML = html;
}


function renderToxicityMetrics(metrics)
{
    const div = document.getElementById("toxicity_metrics");

    if(!div)
    {
        return;
    }

    if(!metrics || !Array.isArray(metrics.labels) || metrics.labels.length === 0)
    {
        div.innerHTML =
        `<p>No toxicity evaluation metrics available.</p>`;
        return;
    }

    const topLabels = metrics.labels.slice(0, 6);

    let html =
    `
    <div class="metrics-card">
        <h3>Toxicity Model Evaluation</h3>
        <p><strong>Average</strong> Accuracy: ${metrics.average["Accuracy"]}, F1: ${metrics.average["F1 Score"]}, ROC-AUC: ${metrics.average["ROC-AUC"]}</p>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Label</th>
                    <th>Best Model</th>
                    <th>Accuracy</th>
                    <th>F1</th>
                    <th>ROC-AUC</th>
                </tr>
            </thead>
            <tbody>
                ${topLabels.map(item =>
                    `
                    <tr>
                        <td>${item.label}</td>
                        <td>${item.best_model}</td>
                        <td>${item.accuracy}</td>
                        <td>${item.f1}</td>
                        <td>${item.auc}</td>
                    </tr>
                    `
                ).join("")}
            </tbody>
        </table>
        <p class="metrics-note">Showing top 6 toxicity labels. Full report available in datasets/model_summary.csv.</p>
    </div>
    `;

    div.innerHTML = html;
}


// =====================================================
// MOLECULAR AI TAB
// =====================================================

function updateMolecular(data)
{
    const mol =
        document
        .getElementById(
            "mol_structure"
        );

    if(
        mol &&
        data.molecule_image
    )
    {
        mol.innerHTML =
        `
        <img
            src="data:image/png;base64,${data.molecule_image}"
            alt="Molecule Structure"
        >
        `;
    }

    const desc =
        document
        .getElementById(
            "descriptor_view"
        );


    if(
        desc &&
        data.dual_view
    )
    {
        let html = "";

        Object.entries(
            data.dual_view.descriptor || {}
        )
        .forEach(([k,v]) =>
        {
            html +=
            `
            <p>
                <b>${k}</b> :
                ${v}
            </p>
            `;
        });

        html +=
        `
        <hr><br>
        <h4>
            Structural View
        </h4>
        `;

        Object.entries(
            data.dual_view.structural || {}
        )
        .forEach(([k,v]) =>
        {
            html +=
            `
            <p>
                <b>${k}</b> :
                ${v}
            </p>
            `;
        });

        desc.innerHTML =
            html;
    }
    else if(desc)
    {
        desc.innerHTML =
            `<p>No molecular descriptors available.</p>`;
    }
}


// =====================================================
// FUSION TAB
// =====================================================

function updateFusion(data)
{
    const div =
        document.getElementById(
            "fusion_result"
        );

    if(!div) return;

    const fusion = data.fusion || {};
    const score =
        Math.round(
            data.readiness?.readiness_score || 0
        );

    const gaugeColor = score >= 70
        ? "#4ade80"
        : score >= 40
            ? "#facc15"
            : "#f97316";

    const items = [
        {
            label: "Toxicity",
            value: fusion.toxicity || 0,
            color: "#f97316"
        },
        {
            label: "DDI",
            value: fusion.ddi || 0,
            color: "#facc15"
        },
        {
            label: "Complexity",
            value: fusion.structural || 0,
            color: "#38bdf8"
        },
        {
            label: "Patient Risk",
            value: fusion.patient || 0,
            color: "#4ade80"
        }
    ];

    let listHtml = "";

    items.forEach(item =>
    {
        const width = Math.max(4, Math.min(100, item.value));
        listHtml +=
        `
        <li>
            <span class="fusion-label">${item.label}</span>
            <span>${item.value}%</span>
        </li>
        <div class="fusion-bar-wrap">
            <div class="fusion-bar" style="width:${width}%; background:${item.color};"></div>
        </div>
        `;
    });

    div.innerHTML =
    `
    <div class="fusion-grid">
        <div>
            <ul class="fusion-list">
                ${listHtml}
            </ul>
        </div>
        <div class="fusion-score-card">
            <div class="gauge">
                <svg width="220" height="220">
                    <circle
                        cx="110"
                        cy="110"
                        r="90"
                        class="gauge-bg"
                    />
                    <circle
                        id="gaugeProgress"
                        cx="110"
                        cy="110"
                        r="90"
                        class="gauge-progress"
                        style="stroke:${gaugeColor};"
                    />
                </svg>
                <div class="gauge-value">
                    ${score}
                </div>
                <div class="gauge-status">
                    ${data.readiness?.category || "Awaiting"}
                </div>
            </div>
            <p style="margin-top:24px; color:#cbd5e1;">
                ${data.readiness?.description || "Analysis pending."}
            </p>
        </div>
    </div>
    `;

    const circumference = 565;
    const offset =
        circumference -
        (score / 100) *
        circumference;

    const progress =
        document.getElementById(
            "gaugeProgress"
        );

    if(progress)
    {
        progress.style.strokeDashoffset = offset;
        progress.style.stroke = gaugeColor;
    }
}


// =====================================================
// SHAP TAB
// =====================================================

function updateSHAP(data)
{
    const div =
        document
        .getElementById(
            "shap_result"
        );

    if(!div) return;

    let html = "";

    if(data.shap_image)
    {
        html +=
        `
        <div class="shap-image-wrapper">
            <img
                src="data:image/png;base64,${data.shap_image}"
                alt="SHAP Explanation"
            >
        </div>
        `;
    }

    if(Array.isArray(data.shap_features) && data.shap_features.length > 0)
    {
        html +=
        `
        <div class="shap-top-drivers">
            <h3>Top Risk Drivers</h3>
            <ul>
                ${data.shap_features.map(feature =>
                    `<li>
                        <strong>${feature.feature}</strong>
                        <span class="shap-direction">${feature.direction === "TOXIC" ? "↑" : "↓"}</span>
                        <div class="shap-value">Value: ${Number(feature.shap_val).toFixed(6)}</div>
                    </li>`
                ).join("")}
            </ul>
        </div>
        `;
    }

    if(!html)
    {
        html =
        `<p>SHAP explanations will appear once analysis completes.</p>`;
    }

    div.innerHTML =
        html;
}


// =====================================================
// RECOMMENDATIONS TAB
// =====================================================

function updateRecommendations(data)
{
    const div =
        document
        .getElementById(
            "recommendation_result"
        );

    if(!div) return;

    let html =
    `
    <h3>
        Dosage Recommendation
    </h3>

    <p>
        <b>
        ${data.dosage.recommendation}
        </b>
    </p>

    <br>

    <p>
        Dose Ratio:
        ${data.dosage.dose_ratio}
    </p>

    <hr>

    <h3>
        Clinical Recommendations
    </h3>

    <ul>
    `;

    data.recommendations
    .forEach(item =>
    {
        html +=
        `<li>${item}</li>`;
    });

    html +=
    `
    </ul>
    `;

    div.innerHTML =
        html;
}