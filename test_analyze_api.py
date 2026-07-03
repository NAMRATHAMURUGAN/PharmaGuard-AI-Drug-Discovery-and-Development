# test_analyze_api.py

import requests

payload = {
    "drug_name":"Aspirin",
    "co_drug":"Warfarin",
    "smiles":"CC(=O)Oc1ccccc1C(=O)O",
    "age":45,
    "weight":70,
    "egfr":80,
    "alt":30,
    "ast":25,
    "gender":"male",
    "conditions":""
}

r = requests.post(
    "http://127.0.0.1:5000/analyze",
    json=payload
)

print(r.status_code)
print(r.json())