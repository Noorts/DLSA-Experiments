import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy
import os

plt.style.use([
    os.path.join(os.path.dirname(__file__), "../resources/vu.mplstyle"),
    os.path.join(os.path.dirname(__file__), "../resources/twocolumn.mplstyle"),
])

FIGURE_DIR = os.path.join(os.path.dirname(__file__), "../../figures/")

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

s1 = [1,2,4,8]
t_32 = [429.45, 229.134, 132.48, 125.06]
t_32_efficiency = [t_32[0] / t_32[i] / s1[i] * 100 for i in range(len(t_32))]
t_16 = [220.02, 118.76, 68.88, 61.62]
t_16_efficiency = [t_16[0] / t_16[i] / s1[i] * 100 for i in range(len(t_16))]
t_8 = [98.9, 54.54, 30.33, 26.20]
t_8_efficiency = [t_8[0] / t_8[i] / s1[i] * 100 for i in range(len(t_8))]
t_L = [5.41, 2.96, 2.66, 2.73]
t_L_efficiency = [t_L[0] / t_L[i] / s1[i] * 100 for i in range(len(t_L))]

# t_rust_L = [4.98, 2.68, 1.84, 1.31]
# t_rust_L_efficiency = [t_rust_L[0] / t_rust_L[i] / s1[i] * 100 for i in range(len(t_rust_L))]
# t_rust_speedup = [t_rust_L[0] / t_rust_L[i] for i in range(len(t_rust_L))]
### CREATE PLOT ###

# t_rust_XL = [167.00, 86.54, 48.82, 43.13]
# t_rust_XL_efficiency = [t_rust_XL[0] / t_rust_XL[i] / s1[i] * 100 for i in range(len(t_rust_XL))]
# t_rust_XL_speedup = [t_rust_XL[0] / t_rust_XL[i] for i in range(len(t_rust_XL))]

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)

# (s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_988e281_synthetic_32000/result_2024-01-02_12-06-09_combined.json')
ax.plot(s1, t_32_efficiency, label=f"Synthetic 32.000", marker='o', linestyle='-')

# (s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_988e281_synthetic_16000/result_2024-01-02_10-10-23.json')
ax.plot(s1, t_16_efficiency, label=f"Synthetic 16.000", marker='o', linestyle='-')

# (s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_4a8ac27_synthetic_8000/result_2023-12-27_14-34-28.json')
ax.plot(s1, t_8_efficiency, label=f"Synthetic 8.000", marker='o', linestyle='-')

# (s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_f748803_XL/result_2023-12-26_12-49-59.json')
ax.plot(s1, t_L_efficiency, label=f"Large", marker='o', linestyle='-')

# ax.plot(s1, t_rust_XL_efficiency, label=f"XL", marker='o', linestyle='-')
# (s, n, n_statistic, n_statistic_normalized) = parse_results('./DAS5/strong_scalability_988e281_large/result_2024-01-02_09-41-58.json')
# ax.plot(s, n_statistic_normalized, label=f"Large", marker='o', linestyle='-')

ax.set_xlabel("Number of Cores")
ax.set_ylabel("Parallel Efficiency (%)")
ax.set_xticks([2 ** i for i in range(4)])
ax.set_yticks([20 * i for i in range(6)])

ax.legend()

fig.tight_layout()
fig.savefig(os.path.join(FIGURE_DIR, "strong_scalability_percentage_threads_go.pdf"))

plt.show()
