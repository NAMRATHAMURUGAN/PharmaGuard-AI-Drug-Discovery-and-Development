# import pandas as pd
# import glob

# all_files = glob.glob("datasets/ddinter_downloads_code_*.csv")
# df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
# df.to_csv("datasets/ddinter_merged.csv", index=False)
# print(f"Merged shape: {df.shape}")
# print(df.head())

# import glob, pandas as pd

# path = r"D:\PHARMAGUARD_AI\PharmaGuardAI\datasets"
# all_files = glob.glob(f"{path}/ddinter_downloads_code_*.csv")

# if not all_files:
#     raise FileNotFoundError("No ddinter_downloads_code_*.csv files found!")

# df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
# df.to_csv(f"{path}/ddinter_merged.csv", index=False)
# print("Merged dataset saved as ddinter_merged.csv")


import pandas as pd
import glob

# Find all CSVs in datasets/ with names like ddinter_downloads_code_A.csv, etc.
all_files = glob.glob("datasets/ddinter_downloads_code_*.csv")

# Merge them into one DataFrame
df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

# Save the merged dataset
df.to_csv("datasets/ddinter_merged.csv", index=False)

print(f"Merged shape: {df.shape}")
print(df.head())

