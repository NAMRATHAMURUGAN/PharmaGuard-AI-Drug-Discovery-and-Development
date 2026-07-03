import pandas as pd

df = pd.read_csv("datasets/ddinter_merged.csv")

drugs = set(df["Drug_A"]).union(set(df["Drug_B"]))

print("Unique Drugs:", len(drugs))