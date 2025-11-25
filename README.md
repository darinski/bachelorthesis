# Privacy-Preserving Logistic Regression with MP-SPDZ

This repository contains the implementation developed as part of a bachelor thesis on privacy-preserving logistic regression using Secure Multi-Party Computation (MPC).  
The core protocol is **MASCOT** executed within the **MP-SPDZ** framework, targeting a **malicious adversary model** in a dishonest-majority setting.

The implementation trains and evaluates logistic regression on **secret-shared data**, using fixed-point arithmetic and a polynomial approximation of the sigmoid function. Results are compared against a plaintext baseline outside of MPC.

---

## Table of Contents

- [Overview](#overview)  
- [Repository Structure](#repository-structure)  
- [System Requirements](#system-requirements)  
- [Installation](#installation)  
- [Running the Pipeline](#running-the-pipeline)  
- [Data and File Formats](#data-and-file-formats)  
- [Implementation Details](#implementation-details)  
- [Notes](#notes)  
- [License](#license)

---

## Overview

The goal of this project is to implement and evaluate **logistic regression under MPC** using:

- the **MASCOT** protocol for offline preprocessing (Beaver triples, MAC material, correlated randomness),  
- the **MP-SPDZ** framework for MPC execution,  
- **fixed-point arithmetic** (`sfix`) and a **polynomial sigmoid approximation** for efficient secure computation.

The implementation focuses on:

- privacy-preserving training and prediction,  
- separation of **offline** (preprocessing) and **online** (secure computation) phases,  
- comparability with a **plaintext logistic regression baseline**.

macOS was used for development and evaluation, particularly because some log-reading scripts and terminal commands are tailored to macOS. Linux should also work with small adjustments.

---



## On Debian/Ubuntu Linux, install the dependencies recommended by MP-SPDZ
sudo apt-get install automake build-essential clang cmake git \
    libboost-dev libboost-filesystem-dev libboost-iostreams-dev \
    libboost-thread-dev libgmp-dev libntl-dev libsodium-dev \
    libssl-dev libtool python3


On macOS, you can install comparable packages via Homebrew:
brew install cmake git boost gmp ntl libsodium openssl libtool python


Python / Conda
It is recommended to use Miniconda to manage the Python environment.
Install Miniconda:
https://docs.conda.io/en/latest/miniconda.html
Create and activate an environment:

conda create -n mp-spdz python=3.10
conda activate mp-spdz

pip install numpy pandas



# Running the Program:
conda activate mp-spdz
python src/offline.py
