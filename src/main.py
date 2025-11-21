import sys, os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parents[1].resolve()       # bachelorthesis folder

ENV_DIR = BASE_DIR / ".venv"
PYTHON = ENV_DIR / "bin/python"                 # path to python inside .env

SRC_DIR = BASE_DIR / "src"

MY_PROGRAM = "thesis"
PREPROCESSING_SCRIPT = "offline.py"

MP_SPDZ_DIR = BASE_DIR / "third_party/MP-SPDZ"              # adjust if your MP-SPDZ folder name differs
MP_SPDZ_SOURCE_DIR = MP_SPDZ_DIR / "Programs/Source"



files_to_link = [PREPROCESSING_SCRIPT, f"{MY_PROGRAM}.mpc"]
DATASET = "trainingPCS"


# =============================
# 1. Activate virtual environment and install packages
# =============================

def setup_env():
    if not ENV_DIR.exists():
        print(f"[INFO] Creating virtual environment at {ENV_DIR}...")
        subprocess.run([sys.executable, "-m", "venv", str(ENV_DIR)], check=True)

    print("Installing required packages...")
    subprocess.run([str(PYTHON), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(PYTHON), "-m", "pip", "install", "-r", str(BASE_DIR / "requirements.txt")], check=True)


# =============================
# 2. Install MP-SPDZ
# =============================

def setup_mpspdz(): 
    if not MP_SPDZ_DIR.exists():
        print(f"[INFO] Cloning MP-SPDZ repository...")
        subprocess.run(["git", "clone", "https://github.com/data61/MP-SPDZ.git", str(MP_SPDZ_DIR)], check=True)

    subprocess.run(["git", "pull"], cwd=str(MP_SPDZ_DIR), check=True)

def build_mpspdz_runtime():
    print("[INFO] Building MP-SPDZ binaries (this may take a while)...")
    subprocess.run(["make", "-j", "8"], cwd=str(MP_SPDZ_DIR), check=True)
    print("[INFO] Build completed.")


# =============================
# 3. Prepare Sources
# ============================

def prepare_sources():
    print("[INFO] Preparing MP-SPDZ source directory...")

    MP_SPDZ_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"       Directory created or already exists: {MP_SPDZ_SOURCE_DIR}")

    for file_name in files_to_link:
        src_file = (SRC_DIR / file_name).resolve()
        target_file = MP_SPDZ_SOURCE_DIR / file_name

        if not src_file.exists():
            raise FileNotFoundError(f"Source file does not exist: {src_file}")

        if target_file.exists() or target_file.is_symlink():
            target_file.unlink()
            
        try:
            if file_name.endswith(".py"):
                subprocess.run(["ln", "-s", str(src_file), str(target_file)], check=True)
                print(f"       Symlink created: {target_file} -> {src_file}")
            elif file_name.endswith(".mpc"):
                subprocess.run(["cp", str(src_file), str(target_file)], check=True)
                print(f"       MPC file copied: {target_file} <- {src_file}")
            else:
                print(f"[WARNING] Skipping unknown file type: {file_name}")
        
        except Exception as e:
            print(f"[ERROR] Could not create symlink for {file_name}: {e}")
            raise
        
def run_preprocessing():
    offline_script = MP_SPDZ_SOURCE_DIR / PREPROCESSING_SCRIPT

    if not offline_script.exists():
        raise FileNotFoundError(f"Symlinked preprocessing script not found: {offline_script}")

    print("[INFO] Running preprocessing script inside MP-SPDZ...")
    subprocess.run([str(PYTHON), str(offline_script), DATASET], cwd=str(MP_SPDZ_DIR), check=True)
    print("[INFO] Preprocessing completed.")

# =============================
# 4. Compile MPC program
# =============================

def compile_mpc():
    print("[INFO] Compiling the MPC program...")
    
    try:
        result = subprocess.run(
            ["./compile.py", MY_PROGRAM],
            cwd=str(MP_SPDZ_DIR),
            check=True,
            text=True,
            capture_output=True
        )
        print("[INFO] Compilation successful.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("[ERROR] Compilation failed.")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        raise SystemExit(1)

# =============================
# 5. Run MPC program with 2 parties
# =============================

def run_mpc():
    n_parties = 2
    processes = []

    print(f"[INFO] Running MPC program ({MY_PROGRAM}) with 2 parties...")
    
    for party_id in range(n_parties):
        cmd = [
            "./mascot-party.x",
            str(party_id),
            MY_PROGRAM,
            "-pn", str(17539),
            "-h", "localhost",
            "-N", str(n_parties)
        ]
        p = subprocess.Popen(cmd, cwd=str(MP_SPDZ_DIR))
        processes.append(p)
        
    for p in processes:
        p.wait()
    
    print("[INFO] MPC execution completed.")

print(BASE_DIR)
print(ENV_DIR)

setup_env()
setup_mpspdz()
build_mpspdz_runtime()
prepare_sources()
run_preprocessing()
compile_mpc()
run_mpc()