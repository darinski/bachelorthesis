import pandas as pd
import sys, os
from pathlib import Path
import secrets
from sklearn.model_selection import train_test_split
import numpy as np

# ===========================================================
# Global constants
# ===========================================================

DEFAULT_SCALE = 2**16 # fixed-point scaling factor for features
RING_P = 2**64 # ring for additive shares, must match MP-SPDZ ring
DEFAULT_TEST_SIZE = 0.2 # default fraction of samples for test set
OUTPUT_DIR = "Player-Data" # MP-SPDZ input directory
DEFAULT_BATCH_SIZE = 1 # not used here, but relevant for MPC training



# ===========================================================
# Helper functions
# ===========================================================

def create_metafile(n_rows_train, n_cols, n_rows_test):
    """
    Create metadata.txt for MP-SPDZ training script.

    Lines:
        1: number of training rows
        2: number of features (excluding label)
        3: number of test rows
        4: batch size (default: 8, can be overwritten later)
        5: number of epochs (default: 2, can be overwritten later)
    """
    metafile_path = os.path.join(OUTPUT_DIR, "metadata.txt")
    with open(metafile_path, "w") as meta_f:
        meta_f.write(f"{n_rows_train}\n")      # number of train data rows
        meta_f.write(f"{n_cols-1}\n")          # number of features
        meta_f.write(f"{n_rows_test}\n")       # number of test data rows
        meta_f.write("8\n")                    # default batch size
        meta_f.write("2\n")                    # default n_epoch

    print(
        f"[create_metafile] n_rows_train={n_rows_train}, "
        f"n_cols={n_cols-1}, n_rows_test={n_rows_test}"
    )


def load_data(name):
     """
    Load a CSV dataset from <project_root>/data_small/{name}.csv and cast to float.

    The function:
    - walks up the directory tree starting from this script
    - finds the first folder that contains 'data_small'
    - loads {name}.csv from that folder

    Raises:
        RuntimeError: if the project root with 'data_small' cannot be found
        FileNotFoundError: if the CSV does not exist
    """

    script_path = Path(__file__).resolve()
    current = script_path.parent
    root = None

    # --- Walk up to find project root containing 'data_small' ---
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

    # --- Load CSV into DataFrame ---
    df = pd.read_csv(data_path, header=None).astype(float)
    return df


def additive_shares(x):
    """
    Generate a random additive sharing of x in Z_{2^64}.

    s0 + s1 ≡ x (mod 2^64)

    Returns:
        tuple[int, int]: (s0, s1)
    """

    s0 = secrets.randbelow(RING_P)
    s1 = (x - s0) % RING_P
    return s0, s1


def to_signed_64(x: int) -> int:
     """
    Map an unsigned 64-bit value in [0, 2^64) to a signed 64-bit integer
    using two's complement representation.
    """

    if x >= 2**63:
        return x - 2**64
    else:
        return x


def save_shares(filename_p0, filename_p1, data, scale: int = DEFAULT_SCALE):
     """
    Secret-share a labeled dataset and write shares to two MP-SPDZ input files.

    For each row:
        - all feature columns are scaled by 'scale' and rounded to int
        - the last column is treated as label and kept as int (e.g., 0/1)
        - each value is split into two additive shares in Z_{2^64}
        - shares are mapped to signed 64-bit (two's complement) for MP-SPDZ

    Parameters:
        filename_p0 : str
            Output filename for party 0 (Input-P0-*)
        filename_p1 : str
            Output filename for party 1 (Input-P1-*)
        data : pd.DataFrame
            Data with features in all columns except last, label in last column.
        scale : int
            Fixed-point scaling factor for feature values.
    """

    with open(filename_p0, "w") as f0, open(filename_p1, "w") as f1:
        n_rows, n_cols = data.shape
        for i in range(n_rows):
            row_p0, row_p1 = [], []
            for j in range(n_cols):
                val = data.iat[i, j]
                if j == n_cols - 1:
                     # last column is label: keep as integer (e.g. 0/1)
                    val = int(val)
                else:
                    # feature columns: encode as fixed-point integer
                    val = int(round(val * scale))

                # generate additive shares
                s0, s1 = additive_shares(val)

                # map to signed 64-bit for MP-SPDZ input
                row_p0.append(to_signed_64(s0))
                row_p1.append(to_signed_64(s1))

            # write rows to files, avoid trailing newline on last line
            f0.write(" ".join(str(x) for x in row_p0) + ("\n" if i != n_rows - 1 else ""))
            f1.write(" ".join(str(x) for x in row_p1) + ("\n" if i != n_rows - 1 else ""))



def check_file_dim(f0, f1):
    """
    Print number of rows and columns for two MP-SPDZ input files.
    Used as a sanity check for train/test share files.
    """
    with open(f0, "r") as file0, open(f1, "r") as file1:
        lines0 = file0.readlines()
        lines1 = file1.readlines()

        cols0 = lines0[0].split()
        cols1 = lines1[0].split()

        print(f"File {f0} has {len(lines0)} rows and {len(cols0)} columns.")
        print(f"File {f1} has {len(lines1)} rows and {len(cols1)} columns.")



# ===========================================================
# Main script
# ===========================================================

if __name__ == "__main__":
    # --- Parse command-line arguments ---
    if len(sys.argv) < 2:
        print("Usage: python offline.py <dataset_name> [scale] [test_size]")
        sys.exit(1)

    dataset_name = sys.argv[1]
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SCALE
    test_size = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_TEST_SIZE

    # --- Ensure output directory exists ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Load dataset and split into train/test ---
    df = load_data(dataset_name)
    df = df.iloc[:, :]
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # -- Split without shuffling to preserve temporal order if any ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )
    train_data = pd.concat([X_train, y_train], axis=1)
    test_data = pd.concat([X_test, y_test], axis=1)

    # --- Secret-share and save train/test datasets ---
    save_shares(
        os.path.join(OUTPUT_DIR, "Input-P0-0"),
        os.path.join(OUTPUT_DIR, "Input-P1-0"),
        train_data,
        scale,
    )
    save_shares(
        os.path.join(OUTPUT_DIR, "Input-P0-1"),
        os.path.join(OUTPUT_DIR, "Input-P1-1"),
        test_data,
        scale,
    )

    # --- Create metadata file ---
    create_metafile(len(train_data), df.shape[1], len(test_data))

    # --- Sanity check: print file dimensions ---
    check_file_dim(
        os.path.join(OUTPUT_DIR, "Input-P0-0"),
        os.path.join(OUTPUT_DIR, "Input-P1-0"),
    )
    check_file_dim(
        os.path.join(OUTPUT_DIR, "Input-P0-1"),
        os.path.join(OUTPUT_DIR, "Input-P1-1"),
    )
