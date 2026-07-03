import pandas as pd

def load_drug_list():
    df = pd.read_csv("datasets/drug_master.csv")

    drugs = (
        df["Drug_Name"]
        .dropna()
        .astype(str)
        .sort_values()
        .tolist()
    )

    return drugs