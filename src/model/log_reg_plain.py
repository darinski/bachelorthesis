import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.preprocessing.datasetLoader import load_breastcancer_data
import numpy as np

df = load_breastcancer_data()
print(df.head())
