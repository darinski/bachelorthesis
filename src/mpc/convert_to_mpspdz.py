# dataset converting into MP-SPDZ input format

# load data
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.preprocessing.datasetLoader import load_data
import numpy as np

df = load_data("trainingLBW")  # change if needed
