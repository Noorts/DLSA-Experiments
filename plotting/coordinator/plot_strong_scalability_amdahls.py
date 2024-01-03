import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy

def amdahl(s, p):
    return 1 / ((1-p) + (p/s))


### PARSE RESULT FILE ###

# Path to your JSON file
json_file_path = './DAS5/strong_scalability_988e281_synthetic_32000/result_2024-01-02_12-06-09_combined.json'

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

n_statistic = np.median(n, axis=1)

n_statistic_normalized = copy.deepcopy(n_statistic) # Normalized = speed up.
for i in range(len(n_statistic) - 1):
    n_statistic_normalized[i + 1] = n_statistic_normalized[0] / n_statistic_normalized[i + 1]
n_statistic_normalized[0] = 1 # [0] so 1 processor (the "sequential") is used as a speed up of 1 baseline.

n_normalized = n_statistic[0] / n # All the individual measurements (not the statistic) are converted to a speed up here.
# Standard deviation of the speed up measurements.
n_std = [np.std(arr) for arr in n_normalized]


### CREATE PLOT ###

# with plt.style.context(["~/dev/latexclass/matplotlib/vu.mplstyle", "~/dev/latexclass/matplotlib/twocolumn.mplstyle"]):
colors = ['#0077B3', '#4FAF48', '#E8692D', '#8E4DA4', '#F2BA2F', '#D4CAC8', '#575756', '#003F6C']

plt.figure(figsize=(4, 3), dpi=600)

# Enable if you want to plot the individual measurements.
# for index, iteration in enumerate(list(zip(*n_normalized))):
#     if index == 0:
#         plt.scatter(s, iteration, color=colors[2], label="Measured")
#     else:
#         plt.scatter(s, iteration, color=colors[2])

popt, pcov = scipy.optimize.curve_fit(amdahl, s, n_statistic_normalized)
print("popt", popt, "pcov", pcov)

plt.errorbar(s, n_statistic_normalized, yerr=n_std, color=colors[1], fmt="o", label="Median (with std.dev.)", capsize=3) # Or fmt="_" for a standard error bar.
n1 = np.linspace(s[0], s[-1], 100000)
plt.plot(n1, amdahl(n1, *popt), color=colors[1], ls="--", label=f"Amdahl's Law (p={round(popt[0], 2)})")

plt.plot([s[0], s[-1]], [s[0], s[-1]], color=colors[0], label="Linear Speedup")
plt.legend()

plt.title("Strong Scalability (32.000 alignments)")
plt.xlabel("Number of Nodes")
plt.ylabel("Speed up")
plt.xticks([2 ** i for i in range(5)])
plt.ylim(0, 4)

plt.tight_layout()
plt.savefig("plotting/strong_scalability_amdahls.png")
