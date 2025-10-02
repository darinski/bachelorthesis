# Bachelor Thesis

This repository contains the implementation of my bachelor thesis.  
**Title:** _"Privacy-Preserving Logistic Regression Training using Multi-Party Computation in a Malicious Setting"_

_Chair of Theoretical Computer Science_  
_University of Mannheim_

## Structure

-   `data/` - raw and processed data used for training (ignored in Git)
-   `results/`- results, figures, and analysis outputs
-   `src/` - implementation (data preprocessing, MPC, training, evaluation, etc.)
-   `tests/`- unit tests

## Data Requirements

-

## MP-SPDZ

cd ..
git clone https://github.com/data61/MP-SPDZ.git
cd MP-SPDZ
make -j8
make libote

To run the repo the creation of a my*mpc file (name changeable) is necessary.
For that, after cloning the MP-SPDZ repo from github in a third_party folder run from inside *third_party/MP-SPDZ/Programs/Source* following command:

```bash
ln -s ../../../../src/mpc my_mpc
```
To check if everything went right run **ls -l** and check for 
```bash
my_mpc -> ../../../../src/mpc
```

Also, make sure you have following structure of your Repo (some folders aren't shown for iverview reasons):
```text
bachelorthesis
- .venv/
- data
-- trainingLBW.csv
-src
-- mpc
--- convert_to_mpspdz.mpc
-- preprocessing
--- datasetLoader.py
- third_party
-- MP_SPDZ
--- Programs
---- Source
----- my_mpc
------convert_to_mpspdz.mpc
--- Scripts
```

With that you should be able to run compile the convert_to_mpspdz.mpc file in the src/mpc folder with like following:
In **/bachelorthesis/src/mpc** run:
```bash
../../third_party/MP-SPDZ/Scripts/compile-run.py -E ring my_mpc/convert_to_mpspdz
```

### OT

In third_party folder execute
```bash
brew install cmake # in bacherlorthesis folder
git clone https://github.com/osu-crypto/libOTe.git # in third_party folder 
cd libOTe 
git submodule update --init --recursive # in libOTe folder
python3 build.py --all --boost --sodium # in libOTe folder
# tell MP-SPDZ where libOTe lives
export LIBOTE_ROOT=~/bachelorthesis/third_party/libOTe 
export CRYPTOTOOLS_ROOT=~/bachelorthesis/third_party/libOTe/cryptoTools

```
[Github libOTe for more details](https://github.com/osu-crypto/libOTe)



In MPC folder execute
```bash
make -j8
make libote
```


### Example Run tutorial
in *~/git/bachelorthesis/third_party/MP-SPDZ*
- **terminal 0**
```bash
./compile.py tutorial 
```
- **terminal 1** 
```bash
./mascot-party.x -p 0 -N 2 --ip-file-name hosts.txt -pn 6000 tutorial 
```
- **terminal 2**
```bash
./mascot-party.x -p 1 -N 2 --ip-file-name hosts.txt -pn 6000 tutorial 
```
