# check_aspirin.py

import pickle

with open("datasets/smiles_lookup.pkl","rb") as f:
    lookup = pickle.load(f)

for drug in lookup.keys():
    if "asp" in drug.lower():
        print(drug)