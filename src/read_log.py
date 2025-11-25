import re
import os

# print(os.listdir('.'))
logfile = "logs/trainingPCS_b8_p0.log"
with open(logfile, "r") as f:
    log_text = f.read()

# ------------------------
# Extract times (online/offline/idle)
# ------------------------
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
    idle_time = float(match.group(4))  # <- wait, let's check

    print("Threads:", num_threads)
    print("Online:", online_time)
    print("Offline:", offline_time)
    print("Idle:", idle_time)

# ------------------------
# Extract data sent (MB)
# ------------------------
data_sent_pattern = re.compile(r"Data sent = ([\d\.]+) MB in ~[\d]+ rounds")
global_sent_pattern = re.compile(r"Global data sent = ([\d\.]+) MB")
data_sent = float(data_sent_pattern.search(log_text).group(1))
global_sent = float(global_sent_pattern.search(log_text).group(1))
print("Data sent:", data_sent, "Global data sent:", global_sent)

# ------------------------
# Extract triples / bits / edaBits / daBits / input tuples
# ------------------------
triples_pattern = re.compile(r"\s+(\d+)\s+Triples")
edaBits_pattern = re.compile(r"\s+~?(\d+)\s+edaBits of size \d+")
daBits_pattern = re.compile(r"\s+(\d+)\s+daBits")
input_tuples_pattern = re.compile(r"\s+(\d+)\s+Input tuples")

triples = sum(int(x) for x in triples_pattern.findall(log_text))
edaBits = sum(int(x) for x in edaBits_pattern.findall(log_text))
daBits = sum(int(x) for x in daBits_pattern.findall(log_text))
input_tuples = sum(int(x) for x in input_tuples_pattern.findall(log_text))

print("Triples:", triples)
print("edaBits:", edaBits)
print("daBits:", daBits)
print("Input tuples:", input_tuples)

# ------------------------
# Extract train/test loss & accuracy
# ------------------------
train_acc_pattern = re.compile(r"train_acc: ([\d\.]+) \((\d+)/(\d+)\)")
test_acc_pattern = re.compile(r"acc: ([\d\.]+) \((\d+)/(\d+)\)")
loss_pattern = re.compile(r"test loss: ([\d\.\-e\+]+)")

train_acc = [float(m.group(1)) for m in train_acc_pattern.finditer(log_text)]
train_correct = [int(m.group(2)) for m in train_acc_pattern.finditer(log_text)]
train_total = [int(m.group(3)) for m in train_acc_pattern.finditer(log_text)]
test_acc = [float(m.group(1)) for m in test_acc_pattern.finditer(log_text)]
test_correct = [int(m.group(2)) for m in test_acc_pattern.finditer(log_text)]
test_total = [int(m.group(3)) for m in test_acc_pattern.finditer(log_text)]
test_loss = [float(m.group(1)) for m in loss_pattern.finditer(log_text)]

print("Train acc:", train_acc, train_correct, train_total)
print("Test acc:", test_acc, test_correct, test_total)
print("Test loss:", test_loss)