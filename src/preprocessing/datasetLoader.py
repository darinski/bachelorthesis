# build path to load file
import sys
from pathlib import Path

import pandas as pd

# Load any dataset
## Requirements for dataset: cleaned, no missing values

# for already cleanded datasets
def load_data(name):

    project_root = Path(sys.argv[0]).resolve().parents[2] 
    data_path = project_root / "data" / f"{name}.csv"
    # print("[DEBUG] Using project_root:", project_root)
    df = pd.read_csv(data_path)

    return df

load_data("trainingLBW")