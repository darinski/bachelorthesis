# Privacy-Preserving Neural Network Training with MP-SPDZ

This repository implements an **end-to-end MPC (Secure Multi-Party Computation) machine-learning pipeline** based on the **MP-SPDZ** framework.  
It allows private neural-network training using secret sharing, without revealing raw data to any party.

The system was developed and tested primarily on **macOS**, but it also works on **Ubuntu/Linux** with minor adjustments.

---

## Project Overview

The repository contains:

- **Preprocessing pipeline** (`offline.py`)  
  Converts a CSV dataset into **additive shares** in the ring ℤ₂⁶⁴ for MP-SPDZ.

- **Neural network in MPC** (`thesis.mpc`)  
  A custom MP-SPDZ program implementing model forward, backward, SGD, and accuracy evaluation.

- **Experiment manager** (`main.py`)  
  Automates preprocessing → metadata generation → compilation → MPC execution → logging.

- **Log analysis tool** (`read_log.py`)  
  Extracts timing, triple usage, communication cost, and accuracy metrics.

- **MP-SPDZ runtime** (cloned into `third_party/MP-SPDZ`)

- **Generated data** under `Player-Data/`

- **Logs** under `logs/`

---

## Directory Structure

```text
bachelorthesis
- data_small
-- trainingLBW.csv
-- trainingPCS.csv
-- trainingUIS.csv
-src
- results
- main.py
- offline.py
- read_log.py
- thesis.mpc
- third_party
-- MP_SPDZ
```

---

## System Requirements

### macOS (recommended)
Development and testing was done on macOS.  
Some commands (esp. the `script` logging tool) use macOS/BSD syntax.

Install dependencies with Homebrew:

```bash
brew install cmake automake libtool boost gmp ntl libsodium openssl llvm git python


