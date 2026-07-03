import requests

url = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    "compound/name/aspirin/property/"
    "CanonicalSMILES/JSON"
)

try:
    response = requests.get(url, timeout=20)

    print("Status Code:", response.status_code)

    print(response.text[:300])

except Exception as e:
    print("ERROR:")
    print(e)