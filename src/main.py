import sys, os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parents[1].resolve()
SRC_DIR = BASE_DIR / "src"
DATA_DIR = SRC_DIR / "../data_small"

MY_PROGRAM = "thesis"
PREPROCESSING_SCRIPT = "offline.py"

MP_SPDZ_DIR = BASE_DIR / "third_party/MP-SPDZ"
MP_SPDZ_SOURCE_DIR = MP_SPDZ_DIR / "Programs/Source"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

BATCH_SIZES = [8, 32]
EPOCH_NUMBERS = [2] # [5, 10, 20]
CONDA_ENV_NAME = "thesis"

# ------------------------------------------------------


def setup_conda_env():
    # check if environment exists
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


# ------------------------------------------------------
def setup_mpspdz():
    if not MP_SPDZ_DIR.exists():
        print(f"[INFO] Cloning MP-SPDZ repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/data61/MP-SPDZ.git", str(MP_SPDZ_DIR)],
            check=True,
        )
        subprocess.run(
            ["git", "clone", "https://github.com/data61/MP-SPDZ.git", str(MP_SPDZ_DIR)],
            check=True,
        )

    subprocess.run(["git", "pull"], cwd=str(MP_SPDZ_DIR), check=True)


def build_mpspdz_runtime():
    print("[INFO] Building MP-SPDZ binaries (this may take a while)...")
    subprocess.run(["make", "-j", "8"], cwd=str(MP_SPDZ_DIR), check=True)


# ------------------------------------------------------
# Prepare sources
# ------------------------------------------------------
def prepare_sources():
    print("[INFO] Preparing sources...")
    MP_SPDZ_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    for name in [PREPROCESSING_SCRIPT, f"{MY_PROGRAM}.mpc"]:
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


# ------------------------------------------------------
# Compile MPC
# ------------------------------------------------------
def compile_mpc():
    print("[INFO] Compiling MPC program...")
    subprocess.run(["./compile.py", MY_PROGRAM], cwd=str(MP_SPDZ_DIR), check=True)


# ------------------------------------------------------
# Run MPC (NO conda!)
# ------------------------------------------------------
def run_mpc(dataset, batch_size, epochs):

    log0 = LOG_DIR / f"{dataset}_b{batch_size}_e{epochs}_p0.log"
    log1 = LOG_DIR / f"{dataset}_b{batch_size}_e{epochs}_p1.log"

    print(f"[INFO] Running MPC for dataset={dataset}, batch={batch_size}")

    cmd0 = [
        "script",
        str(log0),
        "./mascot-party.x",
        "0",
        MY_PROGRAM,
        "-N",
        "2",
        "-pn",
        "17539",
        "-h",
        "localhost",
        "-v",
        "2",
    ]
    cmd1 = [
        "script",
        str(log1),
        "./mascot-party.x",
        "1",
        MY_PROGRAM,
        "-N",
        "2",
        "-pn",
        "17539",
        "-h",
        "localhost",
        "-v",
        "2",
    ]

    p0 = subprocess.Popen(cmd0, cwd=str(MP_SPDZ_DIR))
    p1 = subprocess.Popen(cmd1, cwd=str(MP_SPDZ_DIR))

    p0.wait()
    p1.wait()

    print(f"[INFO] Finished MPC run (logs saved).")


def run_mpc_parallel(dataset, batch_size, n_epochs):
    n_parties = 2
    processes = []

    for party_id in range(n_parties):
        log_file = (
            MP_SPDZ_DIR / f"party{party_id}_{dataset}_bs{batch_size}_ep{n_epochs}.log"
        )
        cmd = [
            "./mascot-party.x",
            str(party_id),
            MY_PROGRAM,
            "-N",
            str(n_parties),
            "-pn",
            "17539",
            "-h",
            "localhost",
            "-v",
            "2",
        ]
        f = open(log_file, "w")
        p = subprocess.Popen(
            cmd, cwd=str(MP_SPDZ_DIR), stdout=f, stderr=subprocess.STDOUT
        )
        processes.append((p, f))

    # Wait for both to finish
    for p, f in processes:
        p.wait()
        f.close()


def run_mpc2(party_id, log_file):
    cmd = [
        "./mascot-party.x",
        str(party_id),
        MY_PROGRAM,
        "-N",
        "2",
        "-pn",
        "17539",
        "-h",
        "localhost",
        "-v",
        "2",
    ]

    with open(log_file, "w") as logfile:
        process = subprocess.Popen(
            cmd,
            cwd=str(MP_SPDZ_DIR),
            stdout=logfile,  # save ALL stdout
            stderr=logfile,  # save ALL stderr
            text=True,
        )

    return process


def write_params_to_metadata(metadata_file, batch_size, n_epochs):
    lines = metadata_file.read_text().splitlines()
    lines[3] = str(batch_size)  # 4th line: batch_size
    lines[4] = str(n_epochs)  # 5th line: n_epochs
    metadata_file.write_text("\n".join(lines))


# ------------------------------------------------------
# Main
# ------------------------------------------------------
def main():
    #setup_conda_env()  # create conda env and install packages
    #setup_mpspdz()  # clone MP-SPDZ if needed
    #build_mpspdz_runtime()  # build MP-SPDZ binaries
    prepare_sources()  # symlink/copy thesis.mpc, offline.py, etc.
    # run_preprocessing("data/trainingPCS.csv")
    compile_mpc()  # compile MPC program once

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
                # run_mpc_parallel(dataset, bs, e)
                # print("\n--- Running MPC parties in parallel ---")
                # print(f"--- Running with batch size {bs} ---")
                # print(f"--- Running with n_epochs {e} ---")
                # p0 = run_mpc2(0, "party0.log")
                # p1 = run_mpc2(1, "party1.log")

                # p0.wait()
                # p1.wait()

if __name__ == "__main__":
    main()
