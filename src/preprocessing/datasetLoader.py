import pandas as pd

# Load any dataset
## Example: Breast Cancer Wisconsin (Diagnostic) Data Set
## Requirements for dataset: cleaned, no missing values

df = pd.read_csv('data/breastcancer_data.csv')



def load_breastcancer_data():
    df = pd.read_csv('data/breastcancer_data.csv')
    df['diagnosis'] = df['diagnosis'].map({'M': 1, 'B': 0})  # M=1, B=0
    df['diagnosis'] = df['diagnosis'].astype(int)
    df = df.drop(columns=['id'])  


    # print("df HEAD:")
    # print(df.head(), "\n")

    # print("df INFO:")
    # print(df.info(), "\n")

    # print("Unique values in 'diagnosis' column:")
    # print(df['diagnosis'].value_counts(), "\n")

    # print("df DESCRIPTION:")
    # print(df.describe(), "\n")

    # print("df SHAPE:")
    # print(df.shape, "\n")

    # print("df COLUMNS:")
    # print(df.columns, "\n")

    # print("df ISNULL:")
    # print(df.isnull().sum(), "\n")

    # print("df DUPLICATES:")
    # print(df.duplicated().sum(), "\n")


    return df
