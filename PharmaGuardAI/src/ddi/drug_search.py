import pandas as pd
from src.ddi.alias_resolver import resolve_alias

# =====================================================
# Load Drug Master
# =====================================================

drug_df = pd.read_csv(
    "datasets/drug_master.csv"
)

DRUG_LIST = sorted(
    drug_df["Drug_Name"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

# =====================================================
# Load Aliases
# =====================================================

alias_df = pd.read_csv(
    "datasets/drug_aliases.csv"
)

ALIAS_MAP = {
    str(row["alias"]).strip().lower():
    str(row["canonical"]).strip()

    for _, row in alias_df.iterrows()
}

# =====================================================
# Alias Resolver
# =====================================================

# def resolve_alias(drug_name):

#     if not drug_name:
#         return None

#     drug_name = drug_name.strip()

#     canonical = ALIAS_MAP.get(
#         drug_name.lower()
#     )

#     if canonical:
#         return canonical

#     return drug_name


# =====================================================
# Search Drugs
# =====================================================

def search_drugs(query, limit=10):

    if not query:
        return []

    query = query.lower().strip()

    starts_with = []
    contains = []

    for drug in DRUG_LIST:

        drug_lower = drug.lower()

        if drug_lower.startswith(query):
            starts_with.append(drug)

        elif query in drug_lower:
            contains.append(drug)

    results = starts_with + contains

    return results[:limit]


# =====================================================
# Check Drug Exists
# =====================================================

DRUG_SET = {
    drug.lower()
    for drug in DRUG_LIST
}

def drug_exists(drug_name):

    canonical = resolve_alias(drug_name)

    if canonical is None:
        return False

    return canonical.lower() in DRUG_SET