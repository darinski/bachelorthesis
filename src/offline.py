import pandas as pd
import sys, os
from pathlib import Path
import secrets
from sklearn.model_selection import train_test_split
import numpy as np

DEFAULT_SCALE = 2**16
DEFAULT_P = 1009 
DEFAULT_TEST_SIZE = 0.2
OUTPUT_DIR = "Player-Data"
DEFAULT_BATCH_SIZE = 1

# ===========================================================
# Helper functions
# ===========================================================


def create_metafile(n_rows_train, n_cols, n_rows_test):
    metafile_path = os.path.join(OUTPUT_DIR, "metadata.txt")
    with open(metafile_path, "w") as meta_f:
        meta_f.write(f"{n_rows_train}\n")  # number of train data rows
        meta_f.write(f"{n_cols-1}\n")  # number of features
        meta_f.write(f"{n_rows_test}\n")  # number of test data rows
        meta_f.write("8\n")  # a default batch size so no error occurs in main.py
        meta_f.write("2\n")  # a default n_epoch so no error occurs in main.py

    print(
        f"[create_metafile] n_rows_train={n_rows_train}, n_cols={n_cols-1}, n_rows_test={n_rows_test}"
    )


def load_data(name):
    """
    Loads a CSV dataset from project_root/data/{name}.csv and converts all values to float.
    """
    script_path = Path(__file__).resolve()

    current = script_path.parent
    root = None

    while current != current.root:
        if (current / "data_small").exists():
            root = current
            break
        current = current.parent

    if root is None:
        raise RuntimeError(
            f"Could not locate project root from script: {script_path}\n"
            f"Walked parents: {list(script_path.parents)}"
        )

    data_path = root / "data_small" / f"{name}.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}\n")

    df = pd.read_csv(data_path, header=None).astype(float)
    # print(df.head())
    return df


def additive_shares(x, p):
    """
    Generate additive shares of x in F_p such that s0 + s1 = x mod p
    """
    s0 = secrets.randbelow(p)
    s1 = (x - s0) % p
    return s0, s1


def check_scale(scale, p):
    if scale >= p:
        scale = scale % p
    return scale


def save_shares(
    filename_p0, filename_p1, data, scale: int = DEFAULT_SCALE, p: int = DEFAULT_P
):
    with open(filename_p0, "w") as f0, open(filename_p1, "w") as f1:
        # print(data.head())
        n_rows, n_cols = data.shape
        # print(n_rows, n_cols)
        for i in range(n_rows):
            row_p0, row_p1 = [], []
            for j in range(n_cols):
                val = data.iat[i, j]
                # print(f"val={val}, row={i}, col={j}")
                if j == n_cols - 1:
                    # last column is label, assume integer
                    val = int(val)
                    # print(f"Label value at row {i}: {val}")
                else:
                    val = int(round(val * scale)) % p
                s0, s1 = additive_shares(val, p)
                row_p0.append(s0)
                row_p1.append(s1)

            f0.write(
                " ".join(str(x) for x in row_p0) + ("\n" if i != n_rows - 1 else "")
            )
            f1.write(
                " ".join(str(x) for x in row_p1) + ("\n" if i != n_rows - 1 else "")
            )


def check_file_dim(f0, f1):
    with open(f0, "r") as file0, open(f1, "r") as file1:
        lines0 = file0.readlines()
        lines1 = file1.readlines()

        for i, (line0, line1) in enumerate(zip(lines0, lines1)):
            cols0 = line0.split()
            cols1 = line1.split()

        print(f"File {f0} has {len(lines0)} rows and {len(cols0)} columns.")
        print(f"File {f1} has {len(lines1)} rows and {len(cols1)} columns.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preprocessing.py <dataset_name> [scale] [p] [test_size]")
        sys.exit(1)

    dataset_name = sys.argv[1]
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SCALE
    p = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_P
    test_size = float(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_TEST_SIZE

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_data(dataset_name)
    df = df.iloc[:10, :]
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )
    train_data = pd.concat([X_train, y_train], axis=1)
    test_data = pd.concat([X_test, y_test], axis=1)

    save_shares(
        os.path.join(OUTPUT_DIR, "Input-P0-0"),
        os.path.join(OUTPUT_DIR, "Input-P1-0"),
        train_data,
        scale,
        p,
    )
    save_shares(
        os.path.join(OUTPUT_DIR, "Input-P0-1"),
        os.path.join(OUTPUT_DIR, "Input-P1-1"),
        test_data,
        scale,
        p,
    )

    create_metafile(
        len(train_data),
        (df.shape[1]),
        len(test_data),
    )

    check_file_dim(
        os.path.join(OUTPUT_DIR, "Input-P0-0"), os.path.join(OUTPUT_DIR, "Input-P1-0")
    )
    check_file_dim(
        os.path.join(OUTPUT_DIR, "Input-P0-1"), os.path.join(OUTPUT_DIR, "Input-P1-1")
    )
    # .reset_index(drop=True)
