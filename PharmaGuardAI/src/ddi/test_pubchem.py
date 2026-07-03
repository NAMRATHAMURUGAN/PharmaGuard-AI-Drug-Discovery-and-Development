import pubchempy as pcp

print("Testing PubChem...")

try:
    compounds = pcp.get_compounds("Abacavir", "name")

    print("Compounds Found:", len(compounds))

    if compounds:
        print("SMILES:")
        print(compounds[0].canonical_smiles)

except Exception as e:
    print("ERROR:")
    print(e)