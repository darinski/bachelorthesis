import re
import os

# ======================================================
# Configuration
# ======================================================

# Path to the log file that should be parsed
logfile = "logs/trainingPCS_b8_p0.log"

# ======================================================
# Load log file
# ======================================================

with open(logfile, "r") as f:
    log_text = f.read()

# ======================================================
# Extract times (online / offline / idle)
# ======================================================

# Pattern for lines like:
# "X threads spent a total of A seconds ... on the online phase,
#  B seconds ... on the preprocessing/offline phase, and
#  C seconds idling"
time_pattern = re.compile(
    r"(\d+) threads spent a total of ([\-0-9\.]+) seconds .*? on the online phase, "
    r"([\-0-9\.]+) seconds .*? on the preprocessing/offline phase, and "
    r"([\-0-9\.]+) seconds idling"
)

match = time_pattern.search(log_text)
if match:
    num_threads = int(match.group(1))
    online_time = float(match.group(2))
    offline_time = float(match.group(3))
    idle_time = float(match.group(4))

    print("Threads:", num_threads)
    print("Online:", online_time)
    print("Offline:", offline_time)
    print("Idle:", idle_time)

# ======================================================
# Extract communication data (MB sent)
# ======================================================

# Example lines:
# "Data sent = X MB in ~Y rounds"
# "Global data sent = Z MB"
data_sent_pattern = re.compile(r"Data sent = ([\d\.]+) MB in ~[\d]+ rounds")
global_sent_pattern = re.compile(r"Global data sent = ([\d\.]+) MB")

data_sent = float(data_sent_pattern.search(log_text).group(1))
global_sent = float(global_sent_pattern.search(log_text).group(1))

print("Data sent:", data_sent, "Global data sent:", global_sent)

# ======================================================
# Extract triples / bits / edaBits / daBits / input tuples
# ======================================================

# Example lines:
# "   12345 Triples"
# "   ~6789 edaBits of size 40"
# "   1000 daBits"
# "   500 Input tuples"
triples_pattern = re.compile(r"\s+(\d+)\s+Triples")
edaBits_pattern = re.compile(r"\s+~?(\d+)\s+edaBits of size \d+")
daBits_pattern = re.compile(r"\s+(\d+)\s+daBits")
input_tuples_pattern = re.compile(r"\s+(\d+)\s+Input tuples")

# Sum über alle passenden Zeilen (falls z.B. mehrere Protokoll-Blöcke vorhanden sind)
triples = sum(int(x) for x in triples_pattern.findall(log_text))
edaBits = sum(int(x) for x in edaBits_pattern.findall(log_text))
daBits = sum(int(x) for x in daBits_pattern.findall(log_text))
input_tuples = sum(int(x) for x in input_tuples_pattern.findall(log_text))

print("Triples:", triples)
print("edaBits:", edaBits)
print("daBits:", daBits)
print("Input tuples:", input_tuples)

# ======================================================
# Extract train/test loss & accuracy
# ======================================================

# Example lines:
# "train_acc: 0.95 (95/100)"
# "acc: 0.90 (90/100)"
# "test loss: 0.1234"
train_acc_pattern = re.compile(r"train_acc: ([\d\.]+) \((\d+)/(\d+)\)")
test_acc_pattern = re.compile(r"acc: ([\d\.]+) \((\d+)/(\d+)\)")
loss_pattern = re.compile(r"test loss: ([\d\.\-e\+]+)")

# Train-Accuracy über alle Epochen
train_acc = [float(m.group(1)) for m in train_acc_pattern.finditer(log_text)]
train_correct = [int(m.group(2)) for m in train_acc_pattern.finditer(log_text)]
train_total = [int(m.group(3)) for m in train_acc_pattern.finditer(log_text)]

# Test-Accuracy über alle Epochen / Ausgaben
test_acc = [float(m.group(1)) for m in test_acc_pattern.finditer(log_text)]
test_correct = [int(m.group(2)) for m in test_acc_pattern.finditer(log_text)]
test_total = [int(m.group(3)) for m in test_acc_pattern.finditer(log_text)]

# Test-Loss-Werte
test_loss = [float(m.group(1)) for m in loss_pattern.finditer(log_text)]

print("Train acc:", train_acc, train_correct, train_total)
print("Test acc:", test_acc, test_correct, test_total)
print("Test loss:", test_loss)
