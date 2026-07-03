import pandas as pd

df = pd.read_csv("datasets/drug_master.csv")

print(df.sample(50, random_state=42).to_string(index=False))

print("\nTotal Drugs:", len(df))