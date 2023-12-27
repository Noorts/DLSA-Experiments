import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy

def amdahl(s, p):
    return 1 / ((1-p) + (p/s))


### PARSE RESULT FILE ###

# Path to your JSON file
json_file_path = './DAS5/strong_scalability_f748803_XL/result_2023-12-26_12-49-59.json'

# Load JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Initialize a dictionary to hold computation times grouped by n_workers
computation_times = {}

# Iterate through the JSON data and group computation times by n_workers
for entry_key, entry_value in data.items():
    n_workers = entry_value['experiment_config']['n_workers']
    if isinstance(entry_value['result'], list):
        for result in entry_value['result']:
            computation_time = result['query_res']['computation_time']

            if n_workers not in computation_times:
                computation_times[n_workers] = []
            computation_times[n_workers].append(computation_time / 1000) # Milliseconds to seconds.


### PROCESS DATA ###

# Convert lists to NumPy arrays
for n_workers in computation_times:
    computation_times[n_workers] = np.array(computation_times[n_workers])

s_raw = {n_workers: np.array(times) for n_workers, times in computation_times.items()}
s = list(s_raw.keys())
n = [s_raw[key] for key in s]

n_means = np.mean(n, axis=1)

n_means_normalized = copy.deepcopy(n_means) # Normalized = parallel efficiency as a percentage.
for i in range(len(n_means) - 1):
    print(n_means_normalized[0], n_means_normalized[i + 1], s[i + 1])
    n_means_normalized[i + 1] = n_means_normalized[0] / n_means_normalized[i + 1] / s[i + 1] * 100
n_means_normalized[0] = 100 # [0] so 1 processor (the "sequential") is as a baseline of 100%.


### CREATE PLOT ###

# with plt.style.context(["~/dev/latexclass/matplotlib/vu.mplstyle", "~/dev/latexclass/matplotlib/twocolumn.mplstyle"]):
colors = ['#0077B3', '#4FAF48', '#E8692D', '#8E4DA4', '#F2BA2F', '#D4CAC8', '#575756', '#003F6C']

plt.figure(figsize=(4, 3), dpi=600)

plt.plot(s, n_means_normalized, color=colors[1], label="Mean", marker='o', linestyle='-')

plt.legend()
plt.title("Strong Scalability")
plt.xlabel("Number of Nodes")
plt.ylabel("Parallel Efficiency (%)")
plt.xticks([2 ** i for i in range(5)])
plt.yticks([20 * i for i in range(6)])

plt.tight_layout()
plt.savefig("plotting/strong_scalability_percentage.png")
