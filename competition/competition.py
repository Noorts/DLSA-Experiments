import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy


### PARSE RESULT FILE ###
def parse_results(json_file_path):
    # Load JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Initialize a dictionary to hold extracted times grouped by n_workers
    extracted_times = {}

    # Iterate through the JSON data and group extracted times by n_workers
    for entry_key, entry_value in data.items():
        n_workers = entry_value['experiment_config']['n_workers']
        if isinstance(entry_value['result'], list):
            for result in entry_value['result']:
                extracted_time = result['query_res']['elapsed_time']

                if n_workers not in extracted_times:
                    extracted_times[n_workers] = []
                extracted_times[n_workers].append(extracted_time)


    ### PROCESS DATA ###

    # Convert lists to NumPy arrays
    for n_workers in extracted_times:
        extracted_times[n_workers] = np.array(extracted_times[n_workers])

    s_raw = {n_workers: np.array(times) for n_workers, times in extracted_times.items()}
    s = list(s_raw.keys())
    n = [s_raw[key] for key in s]

    n_mean = np.mean(n, axis=1)
    n_median = np.median(n, axis=1)
    n_std = [np.std(arr) for arr in n]

    return (s, n, n_mean, n_median, n_std)

results_datasets = [
    'competition/competition_extra_large/result_2024-01-03_14-54-30.json',
    'competition/competition_large/result_2024-01-03_14-24-15.json',
    'competition/competition_medium/result_2024-01-03_14-45-16.json',
    'competition/competition_small/result_2024-01-03_14-50-08.json',
]

print("Elapsed time in milliseconds.")

for outer_index, dataset in enumerate(["XL", "L", "M", "S"]):
    (s, n, n_mean, n_median, n_std) = parse_results(results_datasets[outer_index])
    print("Dataset", dataset)
    for index, n_workers in enumerate([1, 2, 4, 8]): # Hardcoded n_workers in results.
        print("  Workers:", n_workers, "Mean:", n_mean[index], "Median:", n_median[index], "Std.dev.:", n_std[index])

for outer_index, dataset in enumerate(["XL", "L", "M", "S"]):
    (s, n, n_mean, n_median, n_std) = parse_results(results_datasets[outer_index])
    print("Groups of n_workers:", s)
    print("Individual measurements grouped by n_workers:", n)
    print("Dataset", dataset)
    for index, n_workers in enumerate([1, 2, 4, 8]): # Hardcoded n_workers in results.
        print("  Workers:", n_workers, "Mean:", n_mean[index], "Median:", n_median[index], "Std.dev.:", n_std[index])

