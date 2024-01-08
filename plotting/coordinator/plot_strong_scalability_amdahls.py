import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy
import os
from scipy import stats


FIGURE_DIR = os.path.join(os.path.dirname(__file__), "../../figures/")

plt.style.use([
    os.path.join(os.path.dirname(__file__), "../resources/vu.mplstyle"),
    os.path.join(os.path.dirname(__file__), "../resources/twocolumn.mplstyle"),
])

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

res = stats.bootstrap((n_normalized.T,), np.median, confidence_level=0.95)
median = np.median(n_normalized, axis=1)
lower_bound = (median - res.confidence_interval.low)
upper_bound = (res.confidence_interval.high - median)
yerr = np.vstack((lower_bound, upper_bound))

### CREATE PLOT ###

fig = plt.figure()
ax = fig.add_subplot(111)

# Enable if you want to plot the individual measurements.
# for index, iteration in enumerate(list(zip(*n_normalized))):
#     if index == 0:
#         plt.scatter(s, iteration, color=colors[2], label="Measured")
#     else:
#         plt.scatter(s, iteration, color=colors[2])

popt, pcov = scipy.optimize.curve_fit(amdahl, s, n_statistic_normalized)
print("popt", popt, "pcov", pcov)

ax.errorbar(s, n_statistic_normalized, yerr=yerr, fmt=".", label="Median") # Or fmt="_" for a standard error bar.
n1 = np.linspace(s[0], s[-1], 100000)
ax.plot(n1, amdahl(n1, *popt), ls="--", label=f"Amdahl's Law")


ax.set_xlabel("Number of Nodes")
ax.set_ylabel("Speed-up")
ax.set_xticks([2 ** i for i in range(5)])

lim = ax.get_ylim()
ax.plot([s[0], s[-1]], [s[0], s[-1]], label="Linear Speedup")
ax.set_ylim(lim)

ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(FIGURE_DIR, "strong_scalability_amdahls.pdf"))
plt.show()
