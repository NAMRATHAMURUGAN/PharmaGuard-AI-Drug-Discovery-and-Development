from src.ddi.ddi_predictor import predict_ddi
import pandas as pd
import random

df = pd.read_csv("datasets/drug_master.csv")

drugs = df["Drug_Name"].tolist()

counts = {
    "Minor": 0,
    "Moderate": 0,
    "Major": 0
}

for _ in range(200):

    a = random.choice(drugs)
    b = random.choice(drugs)

    try:
        result = predict_ddi(a, b)

        if result["found"]:
            counts[result["level"]] += 1

    except:
        pass

print(counts)