import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy

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

    n_means = np.mean(n, axis=1)

    n_means_normalized = copy.deepcopy(n_means) # Normalized = parallel efficiency as a percentage.
    for i in range(len(n_means) - 1):
        print(n_means_normalized[0], n_means_normalized[i + 1], s[i + 1])
        n_means_normalized[i + 1] = n_means_normalized[0] / n_means_normalized[i + 1] / s[i + 1] * 100
    n_means_normalized[0] = 100 # [0] so 1 processor (the "sequential") is as a baseline of 100%.

    return (s, n, n_means, n_means_normalized)


### CREATE PLOT ###

# with plt.style.context(["~/dev/latexclass/matplotlib/vu.mplstyle", "~/dev/latexclass/matplotlib/twocolumn.mplstyle"]):
colors = ['#0077B3', '#4FAF48', '#E8692D', '#8E4DA4', '#F2BA2F', '#D4CAC8', '#575756', '#003F6C']

plt.figure(figsize=(4, 3), dpi=600)

(s, n, n_means, n_means_normalized) = parse_results('./DAS5/strong_scalability_988e281_synthetic_32000/result_2024-01-02_12-06-09_combined.json')
plt.plot(s, n_means_normalized, color=colors[0], label=f"Synthetic 32.000x", marker='o', linestyle='-')

(s, n, n_means, n_means_normalized) = parse_results('./DAS5/strong_scalability_988e281_synthetic_16000/result_2024-01-02_10-10-23.json')
plt.plot(s, n_means_normalized, color=colors[1], label=f"Synthetic 16.000x", marker='o', linestyle='-')

(s, n, n_means, n_means_normalized) = parse_results('./DAS5/strong_scalability_4a8ac27_synthetic_8000/result_2023-12-27_14-34-28.json')
plt.plot(s, n_means_normalized, color=colors[2], label=f"Synthetic 8.000x", marker='o', linestyle='-')

(s, n, n_means, n_means_normalized) = parse_results('./DAS5/strong_scalability_f748803_XL/result_2023-12-26_12-49-59.json')
plt.plot(s, n_means_normalized, color=colors[3], label=f"Extra Large", marker='o', linestyle='-')

(s, n, n_means, n_means_normalized) = parse_results('./DAS5/strong_scalability_988e281_large/result_2024-01-02_09-41-58.json')
plt.plot(s, n_means_normalized, color=colors[4], label=f"Large", marker='o', linestyle='-')

plt.legend()
plt.title("Strong Scalability")
plt.xlabel("Number of Nodes")
plt.ylabel("Parallel Efficiency (%)")
plt.xticks([2 ** i for i in range(5)])
plt.yticks([20 * i for i in range(6)])

plt.tight_layout()
plt.savefig("plotting/strong_scalability_percentage.png")
