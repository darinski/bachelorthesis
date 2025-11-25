# baseline_plain.py
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

import psutil, os

BASE_DIR = Path(__file__).parents[1].resolve()
DATA_DIR = BASE_DIR / "../data_small"
process = psutil.Process(os.getpid())
def get_mem_mb():
    return process.memory_info().rss / (1024 * 1024)


def run_plaintext_baseline(dataset: str):
    data_path = DATA_DIR / f"{dataset}.csv"
    print(data_path)
    df = pd.read_csv(data_path, header=None).astype(float)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    clf = SGDClassifier(loss="log_loss", max_iter=5, tol=None)

    mem_before = get_mem_mb()
    t0 = time.perf_counter()

    clf.fit(X_train, y_train)

    t1 = time.perf_counter()
    mem_after = get_mem_mb()

    train_pred = clf.predict(X_train)
    test_pred = clf.predict(X_test)

    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)

    print(f"[PLAINTEXT] dataset={dataset}")
    print(f"  runtime: {t1 - t0:.3f} s")
    print(f"  memory_before: {mem_before:.1f} MB")
    print(f"  memory_after:  {mem_after:.1f} MB")
    print(f"  memory_diff:   {mem_after - mem_before:.1f} MB")
    print(f"  train_acc: {train_acc:.3f}")
    print(f"  test_acc:  {test_acc:.3f}")

    return {
        "dataset": dataset,
        "runtime_s": t1 - t0,
        "train_acc": train_acc,
        "test_acc": test_acc,
        "memory_before_mb": mem_before,
        "memory_after_mb": mem_after,
        "memory_diff_mb": mem_after - mem_before,
    }


if __name__ == "__main__":
    run_plaintext_baseline("trainingPCS")