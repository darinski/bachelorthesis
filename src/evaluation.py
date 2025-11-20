import numpy as np
from pathlib import Path

DEFAULT_P = 2**61 - 1
f = 16  

project_root = Path(__file__).resolve().parents[1]
print("Project root:", project_root)
pred_integers = np.loadtxt(f"{project_root}/third_party/MP-SPDZ/Player-Data/predictions.txt", dtype=int)

def signed_from_mod(val, p):
    if val > p // 2:
        return val - p
    return val

def fixed_to_float(val, f=f, p=DEFAULT_P):
    signed_val = signed_from_mod(val, p)
    return signed_val / (2 ** f)


pred_float = [fixed_to_float(x) for x in pred_integers]

pred_labels = [1 if x > 0 else 0 for x in pred_float]

y_test = np.loadtxt("Player-Data/Input-P0-1")[:, -1] + np.loadtxt("Player-Data/Input-P1-1")[:, -1]


accuracy = sum(pred_labels[i] == int(y_test[i]) for i in range(len(y_test))) / len(y_test)
print("Accuracy:", accuracy)