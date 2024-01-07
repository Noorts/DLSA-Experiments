import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy
import os

FIGURE_DIR = os.path.join(os.path.dirname(__file__), "../../figures/")

plt.style.use([
    os.path.join(os.path.dirname(__file__), "../resources/vu.mplstyle"),
    os.path.join(os.path.dirname(__file__), "../resources/twocolumn.mplstyle"),
])

def amdahl(s, p):
    return 1 / ((1-p) + (p/s))


### PARSE RESULT FILE ###
def parse_results(json_file_path):
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

    n_statistic_normalized = copy.deepcopy(n_statistic) # Normalized = parallel efficiency as a percentage.
    for i in range(len(n_statistic) - 1):
        print(n_statistic_normalized[0], n_statistic_normalized[i + 1], s[i + 1])
        n_statistic_normalized[i + 1] = n_statistic_normalized[0] / n_statistic_normalized[i + 1] / s[i + 1] * 100
    n_statistic_normalized[0] = 100 # [0] so 1 processor (the "sequential") is as a baseline of 100%.

    return (s, n, n_statistic, n_statistic_normalized)


### CREATE PLOT ###

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)

(s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_988e281_synthetic_32000/result_2024-01-02_12-06-09_combined.json')
ax.plot(s, n_statistic_normalized, label=f"Synthetic 32000", marker='o', linestyle='-')

(s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_988e281_synthetic_16000/result_2024-01-02_10-10-23.json')
ax.plot(s, n_statistic_normalized, label=f"Synthetic 16000", marker='o', linestyle='-')

(s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_4a8ac27_synthetic_8000/result_2023-12-27_14-34-28.json')
ax.plot(s, n_statistic_normalized, label=f"Synthetic 8000", marker='o', linestyle='-')

(s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_f748803_XL/result_2023-12-26_12-49-59.json')
ax.plot(s, n_statistic_normalized, label=f"Extra Large", marker='o', linestyle='-')

(s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_988e281_large/result_2024-01-02_09-41-58.json')
ax.plot(s, n_statistic_normalized, label=f"Large", marker='o', linestyle='-')

ax.set_xlabel("Number of Nodes")
ax.set_ylabel("Parallel Efficiency (%)")
ax.set_xticks([2 ** i for i in range(5)])
ax.set_yticks([20 * i for i in range(6)])

fig.legend()

fig.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, "strong_scalability_percentage.pdf"))
plt.show()
