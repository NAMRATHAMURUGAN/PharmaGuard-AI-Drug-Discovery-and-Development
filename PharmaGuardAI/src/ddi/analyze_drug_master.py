import pandas as pd

pd.set_option('display.max_rows', None)

df = pd.read_csv("datasets/drug_master.csv")

print(df.head(100))

print("\nTotal Drugs:", len(df))