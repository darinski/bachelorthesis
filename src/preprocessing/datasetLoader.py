import pandas as pd

df = pd.read_csv('data/breastcancer_data.csv')

print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())
