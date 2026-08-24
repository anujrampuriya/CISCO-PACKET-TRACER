import pandas as pd

file_path = "data/cases.csv"

df = pd.read_csv(file_path)

print("Total cases:", len(df))
print("Columns:", list(df.columns))

print("\nFirst case:")
print(df.iloc[0])
