import subprocess

def main():
    # ============================
    # Parse command line arguments
    # ============================

    # not enough arguments
    if len(args) <2:
        print("Usage: python main.py <number_of_parties>")
        sys.exit(1)

    # parse number of parties
    n_parties = int(args[1])

    # check if number of parties is valid
    if n_parties < 2:
        print("[ERROR] Not enough parties. Number of parties must be at least 2.")
        sys.exit(1)
    
    # ============================
    # Execute Logistic Regression in MPC
    # ============================

    # Step 1: Split dataset into n parties
    print(f"[STEP 1] Splitting dataset into {n_parties} parties...")
    subprocess.run(
        ["python3", "src/mpc/convert_to_mpspdz.py", str(n_parties)],
        check=True
    )

    # Step 2: Compiling the MPC logistic regression program
    print("[STEP 2] Compiling the MPC logistic regression program...")
    subprocess.run(
        ["third_party/MP-SPDZ/compile.py", "src/mpc/log_reg_mpc"],
        check=True
    )

    # Step 3: Generating hosts.txt for localhost execution
    print(f"[STEP 3] Creating hosts.txt with {n_parties} localhost entries...")
    with open("hosts.txt", "w") as f:
        for i in range(n_parties):
            f.write("localhost\n")

    # Step 4: Run MPC players 
    print(f"[STEP 4] Running MPC with {n_parties} players...")

    commands = []
    for i in range(n_parties):
        c = subprocess.Popen([
            f"third_party/MP-SPDZ/mascot-party.x -p{str(i)} -N{str(n_parties)} --ipfile-name hosts.txt -pn 6000 log_reg_mpc",
        ])
        commands.append(c)
    
    for c in commands:
        c.wait()
    
    print("[DONE] MPC logistic regression finished successfully.")

if __name__ == "__main__":
    main()