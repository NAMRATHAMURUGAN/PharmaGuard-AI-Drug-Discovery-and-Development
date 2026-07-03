# Drug Synonyms & Canonical Names Mapping

This document lists all drugs recognized by the PharmaGuard system with their synonyms and canonical names used internally.

## Overview

The system uses a **canonical name** for each drug (stored in SMILES lookup, models, and datasets). When users input a drug name, the system:

1. **Alias Resolution**: Converts common names, abbreviations, and brand names to canonical names.
2. **Casing Normalization**: Preserves exact capitalization from the canonical lookup.
3. **DDI Lookup**: Matches drug pairs against the DDInter database.
4. **SMILES Retrieval**: Looks up molecular structure.

---

## Canonical Drug Names & Synonyms

### Analgesics / NSAIDs

| Canonical Name | Common Names / Aliases |
|---|---|
| **Acetylsalicylic acid** | Aspirin, ASA, Ecotrin, Bufferin, Acetylsalicylic acid |
| **Acetaminophen** | Paracetamol, Tylenol, Panadol, Crocin, Acetaminophen |
| **Ibuprofen** | Advil, Motrin, Ibuprofen |

### Anticoagulants

| Canonical Name | Common Names / Aliases |
|---|---|
| **Warfarin** | Coumadin, Jantoven, Warfarin |

### Antidiabetic Agents

| Canonical Name | Common Names / Aliases |
|---|---|
| **Metformin** | Glucophage, Metformin HCL, Metformin XR, Metformin |

### Statins / Lipid-Lowering

| Canonical Name | Common Names / Aliases |
|---|---|
| **Atorvastatin** | Lipitor, Atorvastatin |
| **Simvastatin** | Zocor, Simvastatin |
| **Rosuvastatin** | Crestor, Rosuvastatin |

### Proton Pump Inhibitors

| Canonical Name | Common Names / Aliases |
|---|---|
| **Omeprazole** | Prilosec, Omeprazole |

### Antibiotics

| Canonical Name | Common Names / Aliases |
|---|---|
| **Amoxicillin** | Augmentin (amoxicillin component), Amoxicillin |

### Diuretics

| Canonical Name | Common Names / Aliases |
|---|---|
| **Furosemide** | Lasix, Furosemide |

### Antidiabetic (Meglitinides)

| Canonical Name | Common Names / Aliases |
|---|---|
| **Glimepiride** | Amaryl, Glimepiride |

---

## How to Add New Drugs

### 1. Update `datasets/drug_aliases.csv`

Add rows in the format:

```csv
alias,canonical
brand_name,Canonical Name
abbreviation,Canonical Name
common_name,Canonical Name
```

**Example:**
```csv
metformin,Metformin
glucophage,Metformin
metformin hcl,Metformin
```

### 2. Ensure Canonical Name exists in `datasets/smiles_lookup.pkl`

- The canonical name **must** match exactly (case-sensitive) the key in SMILES_LOOKUP.
- Example: `"Acetylsalicylic acid"` (not `"Acetylsalicylic Acid"` or `"acetylsalicylic acid"`).

### 3. Verify in DDInter Dataset

- Check `datasets/ddinter_merged.csv` for known interactions.
- Use the canonical name format from column `Drug_A` and `Drug_B`.

---

## Testing Your Synonyms

Run the following to verify:

```python
from src.ddi.alias_resolver import resolve_alias
from src.ddi.ddi_predictor import predict_ddi
import pickle

# Test alias resolution
print(resolve_alias("Aspirin"))  # Should return "Acetylsalicylic acid"

# Verify SMILES lookup
with open('datasets/smiles_lookup.pkl','rb') as f:
    lookup = pickle.load(f)
    print("Acetylsalicylic acid" in lookup)  # Should be True

# Test DDI prediction
result = predict_ddi("Warfarin", "Aspirin")
print(result)  # Should show "Major" interaction
```

---

## Known Issues & Solutions

### Issue: "Drug B Not Found" Error

**Cause**: The drug name entered doesn't match any canonical name in SMILES_LOOKUP.

**Solution**:
1. Check the spelling (case-sensitive).
2. Add the drug to `drug_aliases.csv` if it's a brand name or abbreviation.
3. Ensure the canonical name exists in `smiles_lookup.pkl`.

### Issue: Incorrect DDI Severity

**Cause**: Drug name resolved correctly, but interaction not found in DDInter dataset.

**Solution**:
1. Verify both drugs are in the dataset (check `ddinter_merged.csv`).
2. Check capitalization in the DDInter data vs. resolved names.
3. The system will fall back to ML prediction if lookup fails—check model output.

---

## Current Status

✅ **Fixed**: Alias resolver now preserves canonical name casing.  
✅ **Fixed**: Reverse order DDI lookup (in case dataset stores pairs reversed).  
✅ **Expanded**: Added 20+ common drug aliases and canonical names.  

**Example**:
- Input: `"Warfarin", "Aspirin"`
- Resolved: `("Warfarin", "Acetylsalicylic acid")`
- DDI Result: **Major** (100% severity)
