# share generator with trusted dealer

import random
import argparse
import os
import numpy as np
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent  # = src/
root_dir = src_dir.parent  # = bachelorthesis/
sys.path.append(str(src_dir / "preprocessing"))
print("[DEBUG] Added to sys.path:", str(src_dir / "preprocessing"))

from datasetLoader import load_data

DEFAULT_P = 2**61 - 1


def to_int_field(val, scale, p):
    if val == "":
        raise ValueError("Empty value encountered.")
    else:
        int_val = int(round(float(val) * scale)) % p
        return int_val


def write_matrix(path, matrix):
    with open(path, "w") as f:
        for row in matrix:
            f.write(" ".join(str(x) for x in row) + "\n")


def create_output_dir(path):
    os.makedirs(path, exist_ok=True)


def generate_shares(df, out_dir, p, scale, seed=None):
    if seed is not None:
        random.seed(seed)

    data = df.to_numpy(dtype=float)
    n_rows, n_cols = data.shape
    print(f"[INFO] Loaded dataset with {n_rows} rows and {n_cols} columns")

    alpha = random.randrange(0, p)
    alpha0 = random.randrange(0, p)
    alpha1 = (alpha - alpha0) % p

    shares0 = np.zeros((n_rows, n_cols), dtype=int)
    print("[DEBUG] first shares0 to check: \n", shares0[0:3])
    shares1 = np.zeros((n_rows, n_cols), dtype=int)
    mac0 = np.zeros((n_rows, n_cols), dtype=int)
    mac1 = np.zeros((n_rows, n_cols), dtype=int)

    for i in range(n_rows):
        for j in range(n_cols):
            val = to_int_field(data[i][j], scale, p)
            share0 = random.randrange(0, p)
            share1 = (val - share0) % p
            shares0[i][j] = share0
            shares1[i][j] = share1
            mac0[i][j] = (share0 * alpha0) % p
            mac1[i][j] = (share1 * alpha1) % p

    print("[DEBUG] Sample shares0: \n", shares0[0:2])
    print("[DEBUG] Sample shares1: \n", shares1[0:2])

    create_output_dir(out_dir)

    write_matrix(os.path.join(out_dir, "Input-P0-0"), shares0)
    write_matrix(os.path.join(out_dir, "Input-P1-0"), shares1)

    write_matrix(os.path.join(out_dir, "MAC-P0-0"), mac0)
    write_matrix(os.path.join(out_dir, "MAC-P1-0"), mac1)

    with open(os.path.join(out_dir, "alpha0.txt"), "w") as f:
        f.write(str(alpha0) + "\n")
    with open(os.path.join(out_dir, "alpha1.txt"), "w") as f:
        f.write(str(alpha1) + "\n")

    print(f"[INFO] Wrote Player-Data files to {out_dir}")
    return alpha0, alpha1


def main():
    parser = argparse.ArgumentParser(
        description="Secret-share a dataset for MPC (MASCOT-compatible)."
    )
    parser.add_argument("--dataset", required=True, help="Dataset name (without .csv)")
    parser.add_argument(
        "--out", default="../../Player-Data", help="Output folder for Player-Data"
    )
    parser.add_argument("--p", type=int, default=DEFAULT_P, help="Prime field modulus")
    parser.add_argument(
        "--scale", type=int, default=1, help="Fixed-point scaling factor"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    data_path = root_dir / "data" / f"{args.dataset}.csv"
    out_dir = root_dir / "third_party" / "MP-SPDZ" / "Player-Data"

    print(f"[INFO] Loading dataset from {data_path}")
    df = load_data(args.dataset)

    alpha0, alpha1 = generate_shares(
        df, args.out, p=args.p, scale=args.scale, seed=args.seed
    )

    print(f"[SUCCESS] Generated shares for dataset '{args.dataset}'.")
    print(f"[MAC KEYS] alpha0={alpha0}, alpha1={alpha1}")


if __name__ == "__main__":
    main()
