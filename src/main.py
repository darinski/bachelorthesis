import sys, os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parents[1].resolve()
SRC_DIR = BASE_DIR / "src"
DATA_DIR = SRC_DIR / "../data"

MY_PROGRAM = "thesis"
PREPROCESSING_SCRIPT = "offline.py"

MP_SPDZ_DIR = BASE_DIR / "third_party/MP-SPDZ"
MP_SPDZ_SOURCE_DIR = MP_SPDZ_DIR / "Programs/Source"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

BATCH_SIZES = [8] # [2, 50, 200]
EPOCH_NUMBERS = [5, 10, 20]
CONDA_ENV_NAME = "thesis"

# ------------------------------------------------------
# Prepare sources
# ------------------------------------------------------
def prepare_sources():
    print("[INFO] Preparing sources...")
    MP_SPDZ_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    for name in [PREPROCESSING_SCRIPT, f"{MY_PROGRAM}.mpc", "config.txt"]:
        src_file = SRC_DIR / name
        dst_file = MP_SPDZ_SOURCE_DIR / name

        if dst_file.exists():
            dst_file.unlink()

        if name.endswith(".py"):
            subprocess.run(["ln", "-s", str(src_file), str(dst_file)], check=True)
        else:
            subprocess.run(["cp", str(src_file), str(dst_file)], check=True)

        print(f" -> {name} linked/copied")

# ------------------------------------------------------
# Preprocessing (only part requiring conda)
# ------------------------------------------------------
def run_preprocessing(dataset):
    print(f"[INFO] Preprocessing dataset {dataset}...")

    subprocess.run(
        [
            "conda", "run", "-n", CONDA_ENV_NAME,
            "python", str(MP_SPDZ_SOURCE_DIR / PREPROCESSING_SCRIPT),
            dataset
        ],
        cwd=str(MP_SPDZ_DIR),
        check=True
    )

# ------------------------------------------------------
# Compile MPC
# ------------------------------------------------------
def compile_mpc():
    print("[INFO] Compiling MPC program...")
    subprocess.run(
        ["./compile.py", MY_PROGRAM],
        cwd=str(MP_SPDZ_DIR),
        check=True
    )

# ------------------------------------------------------
# Run MPC (NO conda!)
# ------------------------------------------------------
def run_mpc(dataset, batch_size, epochs):

    log0 = LOG_DIR / f"{dataset}_b{batch_size}_e{epochs}_p0.log"
    log1 = LOG_DIR / f"{dataset}_b{batch_size}_e{epochs}_p1.log"

    print(f"[INFO] Running MPC for dataset={dataset}, batch={batch_size}")

    cmd0 = [
        "script", str(log0),
        "./mascot-party.x", "0", MY_PROGRAM,
        "-N", "2", "-pn", "17539", "-h", "localhost", "-v", "2"
    ]
    cmd1 = [
        "script", str(log1),
        "./mascot-party.x", "1", MY_PROGRAM,
        "-N", "2", "-pn", "17539", "-h", "localhost", "-v", "2"
    ]

    p0 = subprocess.Popen(cmd0, cwd=str(MP_SPDZ_DIR))
    p1 = subprocess.Popen(cmd1, cwd=str(MP_SPDZ_DIR))

    p0.wait()
    p1.wait()

    print(f"[INFO] Finished MPC run (logs saved).")

def write_params_to_metadata(metadata_file, batch_size, n_epochs):
    lines = metadata_file.read_text().splitlines()
    lines[3] = str(batch_size)   # 4th line: batch_size
    lines[4] = str(n_epochs)     # 5th line: n_epochs
    metadata_file.write_text("\n".join(lines))

# ------------------------------------------------------
# Main
# ------------------------------------------------------
def main():
    prepare_sources()   # symlink/copy thesis.mpc, offline.py, etc.
    compile_mpc()       # compile MPC program once

    for csv_file in DATA_DIR.glob("train*.csv"):
        dataset = csv_file.stem
        print(f"\n=== Processing dataset: {dataset} ===")

        # Preprocess once to generate metadata.txt
        run_preprocessing(dataset)
        metadata_file = MP_SPDZ_DIR / "Player-Data/metadata.txt"
        print(metadata_file)
        for bs in BATCH_SIZES:
            for e in EPOCH_NUMBERS:
                print(f"\n--- Running with batch size {bs} ---")
                print(f"\n--- Running with n_epochs {e} ---")

                # Update metadata.txt with current batch size
                write_params_to_metadata(metadata_file, bs, e)

                # Run the MPC program
                run_mpc(dataset, bs, e)

if __name__ == "__main__":
    main()