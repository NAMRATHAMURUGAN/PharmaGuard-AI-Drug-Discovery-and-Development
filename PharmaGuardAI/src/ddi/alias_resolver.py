import pandas as pd

aliases = pd.read_csv(
    "datasets/drug_aliases.csv"
)

ALIAS_MAP = {
    row["alias"].lower():
    row["canonical"]

    for _, row in aliases.iterrows()
}

# Build canonical lookup (preserve exact casing from CSV)
CANONICAL_LOOKUP = {}
for _, row in aliases.iterrows():
    canonical = row["canonical"].strip()
    CANONICAL_LOOKUP[canonical.lower()] = canonical

def resolve_alias(name):

    if not name:
        return name

    name_stripped = name.strip()
    name_lower = name_stripped.lower()

    # Check alias map first (e.g., "aspirin" -> "Acetylsalicylic acid")
    if name_lower in ALIAS_MAP:
        return ALIAS_MAP[name_lower]

    # Check if it's already a canonical name (preserve exact casing)
    if name_lower in CANONICAL_LOOKUP:
        return CANONICAL_LOOKUP[name_lower]

    # Unknown drug: return original input (don't force title case)
    return name_stripped