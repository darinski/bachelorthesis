import sys, os
import subprocess
import time
from pathlib import Path

# =======================================================
# GLobal paths and configuration
# =======================================================

# Project structure
BASE_DIR = Path(__file__).parents[1].resolve()
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data_small"  # adjustable, whene using different datasets

# File / program names
MY_PROGRAM = "thesis"  # name of MP-SPDZ program thesis.mpc
PREPROCESSING_SCRIPT = "offline.py"  # local preprocessing script

# MP-SPDZ paths
MP_SPDZ_DIR = BASE_DIR / "third_party/MP-SPDZ"
MP_SPDZ_SOURCE_DIR = MP_SPDZ_DIR / "Programs" / "Source"

# Logs directory
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# --- Experiment configurations (batch_size, epochs) ---
EXPERIMENTS = [
    (32, 5),
    (128, 5),
    (32, 10),
]

# Conda environment name
CONDA_ENV_NAME = "thesis"


# ======================================================
# Conda environment configuration
# ======================================================

def setup_conda_env():
    """
    Create and configure the dedicated conda environment if missing.
    Installs packages from requirements.txt.
    """
    # --- Check if environment already exists ---
    result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
    if CONDA_ENV_NAME not in result.stdout:
        print(
            f"[INFO] Creating conda environment '{CONDA_ENV_NAME}' with Python {PYTHON_VERSION}..."
        )
        subprocess.run(
            ["conda", "create", "-n", CONDA_ENV_NAME, f"python={PYTHON_VERSION}", "-y"],
            check=True,
        )
        print(
            f"[INFO] Creating conda environment '{CONDA_ENV_NAME}' with Python {PYTHON_VERSION}..."
        )
        subprocess.run(
            ["conda", "create", "-n", CONDA_ENV_NAME, f"python={PYTHON_VERSION}", "-y"],
            check=True,
        )
    else:
        print(f"[INFO] Conda environment '{CONDA_ENV_NAME}' already exists.")

    # --- Activate environment and install packages ---
    print(f"[INFO] Activating conda environment '{CONDA_ENV_NAME}'...")
    conda_prefix = subprocess.run(
        ["conda", "run", "-n", CONDA_ENV_NAME, "echo", "$CONDA_PREFIX"],
        capture_output=True,
        text=True,
        shell=True,
    ).stdout.strip()
    print(f"[INFO] Conda environment path: {conda_prefix}")

    print("[INFO] Installing Python packages from requirements.txt...")
    subprocess.run(
        ["conda", "run", "-n", CONDA_ENV_NAME, "pip", "install", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [
            "conda",
            "run",
            "-n",
            CONDA_ENV_NAME,
            "pip",
            "install",
            "-r",
            str(BASE_DIR / "requirements.txt"),
        ],
        check=True,
    )
    subprocess.run(
        ["conda", "run", "-n", CONDA_ENV_NAME, "pip", "install", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [
            "conda",
            "run",
            "-n",
            CONDA_ENV_NAME,
            "pip",
            "install",
            "-r",
            str(BASE_DIR / "requirements.txt"),
        ],
        check=True,
    )

# ======================================================
# MP-SPDZ setup and execution functions
# ======================================================

def setup_mpspdz():
    """
    Clone MP-SPDZ if missing and pull latest updates.
    """

    # --- Clone MP-SPDZ if missing ---
    if not MP_SPDZ_DIR.exists():
        print(f"[INFO] Cloning MP-SPDZ repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/data61/MP-SPDZ.git", str(MP_SPDZ_DIR)],
            check=True,
        )

    # --- Pull latest updates ---
    print("[INFO] Updating MP-SPDZ...")
    subprocess.run(["git", "pull"], cwd=str(MP_SPDZ_DIR), check=True)


def build_mpspdz_runtime():
    """
    Build MP-SPDZ binaries (compile all runtime code).
    This step can take several minutes.
    """

    print("[INFO] Building MP-SPDZ binaries (this may take a while)...")
    subprocess.run(["make", "-j", "8"], cwd=str(MP_SPDZ_DIR), check=True)



# ======================================================
# Main experiment functions
# ======================================================

def prepare_sources():
    """
    Prepare MP-SPDZ source directory:
    - Ensure Programs/Source exists
    - Symlink the Python preprocessing script into MP-SPDZ
    - Copy the MPC program into MP-SPDZ
    """

    print("[INFO] Preparing sources...")
    MP_SPDZ_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    for name in [PREPROCESSING_SCRIPT, f"{MY_PROGRAM}.mpc"]:
        src_file = SRC_DIR / name
        dst_file = MP_SPDZ_SOURCE_DIR / name

        # Remove old version if present
        if dst_file.exists():
            dst_file.unlink()

        if name.endswith(".py"):
            # symlink Python scripts
            subprocess.run(["ln", "-s", str(src_file), str(dst_file)], check=True)
        else:
            # copy MPC program
            subprocess.run(["cp", str(src_file), str(dst_file)], check=True)

        print(f" -> {name} linked/copied")


def run_preprocessing(dataset):
    """
    Execute offline preprocessing inside MP-SPDZ.
    Generates secret shares + metadata.

    Returns:
        float: execution time in seconds
    """

    print(f"[INFO] Preprocessing dataset {dataset}...")
    t0 = time.perf_counter()

    subprocess.run(
        [
            "conda",
            "run",
            "-n",
            CONDA_ENV_NAME,
            "python",
            str(MP_SPDZ_SOURCE_DIR / PREPROCESSING_SCRIPT),
            dataset,
        ],
        cwd=str(MP_SPDZ_DIR),
        check=True,
    )

    t1 = time.perf_counter()
    print(f"[TIMING] Preprocessing (offline shares) took {t1 - t0:.3f} s")
    return t1 - t0  # offline time


def compile_mpc():
    """
    Compile the MPC program using MP-SPDZ's compile.py.
    """
    print("[INFO] Compiling MPC program...")
    subprocess.run(["./compile.py", MY_PROGRAM], cwd=str(MP_SPDZ_DIR), check=True)


def write_params_to_metadata(metadata_file: Path, batch_size: int, n_epochs: int):
    """
    Overwrite metadata.txt parameters:
    - Line 4: batch_size
    - Line 5: epochs
    """
    lines = metadata_file.read_text().splitlines()
    lines[3] = str(batch_size)  # 4th line: batch_size
    lines[4] = str(n_epochs)  # 5th line: n_epochs
    metadata_file.write_text("\n".join(lines))


def run_mpc(batch_size: int, epochs: int, dataset: str):
    """
    Run mascot-party.x for both parties and log outputs.

    Returns:
        (runtime, log_p0_path, log_p1_path)
    """

    exp_name = f"{dataset}_B{batch_size}_E{epochs}"
    log0 = LOG_DIR / f"{exp_name}_p0.log"
    log1 = LOG_DIR / f"{exp_name}_p1.log"

    print(f"[INFO] Running MPC for {exp_name}")

    # Party 0 command
    cmd0 = [
        "script",
        str(log0),
        "./mascot-party.x",
        "0",
        MY_PROGRAM,
        "-N",
        "2",
        "-pn",
        "17540",
        "-h",
        "localhost",
        "-v",
        "2",
    ]
    # Party 1 command
    cmd1 = [
        "script",
        str(log1),
        "./mascot-party.x",
        "1",
        MY_PROGRAM,
        "-N",
        "2",
        "-pn",
        "17540",
        "-h",
        "localhost",
        "-v",
        "2",
    ]

    # --- Run both parties ---
    t0 = time.perf_counter()
    p0 = subprocess.Popen(cmd0, cwd=str(MP_SPDZ_DIR))
    p1 = subprocess.Popen(cmd1, cwd=str(MP_SPDZ_DIR))

    p0.wait()
    p1.wait()
    t1 = time.perf_counter()

    total = t1 - t0
    print(f"[TIMING] MPC run {exp_name} took {total:.3f} s")
    print(f"[INFO] Logs written to {log0} and {log1}")
    return total, log0, log1

# ======================================================
# Main execution
# ======================================================

def main():
     """
    Full execution pipeline:
    1) Prepare sources
    2) Preprocess dataset once
    3) Compile program once
    4) Run all MPC experiments with varied parameters
    5) Print summary
    """
    # --- Step 1: Prepare MP-SPDZ sources (thesis.mpc, offline.py) ---
    prepare_sources()

    # --- Step 2: Choose dataset (e.g., “trainingPCS” or whatever your 500-row file is) ---
    dataset = "trainingUIS"  # adjust name to your CSV stem

    # --- Step 3: Preprocessing once to generate shares & initial metadata ---
    offline_time = run_preprocessing(dataset)

    # --- Step 4: Compile MPC once ---
    compile_mpc()

    metadata_file = MP_SPDZ_DIR / "Player-Data" / "metadata.txt"

    # --- Step 5: Run our three MPC configurations ---
    results = []  # collect for later printing

    for batch_size, epochs in EXPERIMENTS:
        print(f"\n=== Experiment B={batch_size}, E={epochs} ===")

        # Update metadata with current batch size & epochs
        write_params_to_metadata(metadata_file, batch_size, epochs)

        # Run MPC
        total_time, log0, log1 = run_mpc(batch_size, epochs, dataset)

        # Store results
        results.append(
            {
                "dataset": dataset,
                "B": batch_size,
                "E": epochs,
                "offline_time_s": offline_time,
                "mpc_total_time_s": total_time,
                "log_p0": str(log0),
                "log_p1": str(log1),
            }
        )

    # --- Step 6: Print summary of all experiments ---
    print("\n=== Summary of MPC experiments ===")
    for r in results:
        print(
            f"{r['dataset']} | B={r['B']}, E={r['E']} | "
            f"offline={r['offline_time_s']:.3f}s, total={r['mpc_total_time_s']:.3f}s"
        )


if __name__ == "__main__":
    main()
