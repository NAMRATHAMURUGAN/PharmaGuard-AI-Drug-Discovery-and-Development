# ============================================================
# PHARMAGUARD AI
# Dual View Molecular Analysis
# ============================================================

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator


MORGAN_GENERATOR = GetMorganGenerator(
    radius=2,
    fpSize=1024
)


def dual_view_analysis(smiles: str):
    """
    Returns descriptor view + structural view
    for dashboard visualization.
    """

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return {
            "descriptor": {},
            "structural": {}
        }

    descriptor_view = {

        "Molecular Weight":
            round(Descriptors.MolWt(mol), 2),

        "LogP":
            round(Descriptors.MolLogP(mol), 2),

        "TPSA":
            round(rdMolDescriptors.CalcTPSA(mol), 2),

        "HBA":
            rdMolDescriptors.CalcNumHBA(mol),

        "HBD":
            rdMolDescriptors.CalcNumHBD(mol)
    }

    fp = MORGAN_GENERATOR.GetFingerprint(mol)

    on_bits = len(fp.GetOnBits())

    structural_view = {

        "Atoms": mol.GetNumAtoms(),

        "Bonds": mol.GetNumBonds(),

        "Fingerprint Type":
            "Morgan Fingerprint",

        "Fingerprint Size":
            1024,

        "Radius":
            2,

        "Active Bits":
            on_bits
    }

    return {
        "descriptor": descriptor_view,
        "structural": structural_view
    }


# ------------------------------------------------------------
# Testing
# ------------------------------------------------------------

if __name__ == "__main__":

    result = dual_view_analysis(
        "CC(=O)Oc1ccccc1C(=O)O"
    )

    print(result)