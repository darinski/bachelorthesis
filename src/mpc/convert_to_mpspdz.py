# dataset converting into MP-SPDZ input format

# # - Build path to load file -
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
# print("[DEBUG] Using project_root:", project_root)

# - Converting -
from src.preprocessing.datasetLoader import load_data
import numpy as np
from sklearn.model_selection import train_test_split
import shutil

# -- Arguments --
n_parties = int(sys.argv[1])  # number of parties typed in console argument
S = 2**16  # scaling factor (LogReg with float, but MP-SPDZ only int)

# -- Load Data --
df = load_data("trainingLBW")  # change if needed
X = df.drop(columns=[df.columns[-1]], axis=1)  # features
y = df.iloc[:, -1]  # target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, random_state=0
)  # spilt into training and test set

X_train_scaled = (X_train.to_numpy() * S).astype(int)
y_train_scaled = (y_train.to_numpy() * S).astype(int)

n_features = X_train.shape[1]

# -- Shuffle feature indices --
rng = np.random.default_rng(seed=42) 
shuffled_cols = rng.permutation(n_features)
print("Shuffled feature indices: ", shuffled_cols)

# -- Partition across parties --
feature_parties = n_features - 1
splits = np.array_split(
    shuffled_cols, n_parties -1
) 

print("Splits: ", splits)

# -- Save data in MP-SPDZ format --
output_dir = Path("Player-Data")
if Path(output_dir).exists():
    shutil.rmtree(output_dir)  # remove existing directory and files
Path("Player-Data").mkdir(parents=True, exist_ok=True)

for i, cols in enumerate(splits):
    X_i_train_part = (
        X_train_scaled[:, cols]
        if cols.size > 0
        else np.empty((X_train_scaled.shape[0], 0), dtype=int)
    )
    np.savetxt(f"Player-Data/Input-P{i}-0", X_i_train_part, fmt="%d")

# last party gets the target column
np.savetxt(f"Player-Data/Input-P{n_parties-1}-0", y_train_scaled, fmt="%d")
print(f"Data successfully converted and saved for {n_parties} parties.")
