#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
import json
import numpy as np
import scipy as sp
from scipy import stats
import sys
import os

plt.style.use([
    os.path.join(os.path.dirname(__file__), "../resources/vu.mplstyle"),
    os.path.join(os.path.dirname(__file__), "../resources/twocolumn.mplstyle"),
])

RESULT_DIR = os.path.join(os.path.dirname(__file__), "../../LOCAL/algorithm_unknown/")
FIGURE_DIR = os.path.join(os.path.dirname(__file__), "../../figures/")

LANE_COUNT = 32

def amdahl(s, p):
    return 1 / ((1-p) + (p/s))

def main():
    if len(sys.argv) > 1:
        print("Using result directory", sys.argv[1])
        global RESULT_DIR
        RESULT_DIR = sys.argv[1]
    else:
        print("No result directory provided, assuming", RESULT_DIR)

    plot_lane_scaling_target("simd_lanes_ringbuf")

    plt.show()

def plot_lane_scaling_target(directory):
    sequential_result = read_file(os.path.join(RESULT_DIR, "sequential.json"))
    sequential_cups = get_cups(sequential_result) / 1e6

    # Create (emtpy) figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Lane count")
    ax.set_ylabel("Speedup")
    ax.yaxis.set_minor_locator(MultipleLocator(1))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    plot_colors = {
        "disjoint": colors[0],
        "random": colors[1],
        "equal": colors[2],
    }

    plot_markers = {
        "disjoint": "x",
        "random": ".",
        "equal": "*",
    }

    for target_name in ["disjoint", "random", "equal"]:
        files = [
            (1, f"{directory}/{target_name}/01.json"),
            (2, f"{directory}/{target_name}/02.json"),
            (4, f"{directory}/{target_name}/04.json"),
            (8, f"{directory}/{target_name}/08.json"),
            (16, f"{directory}/{target_name}/16.json"),
            (32, f"{directory}/{target_name}/32.json"),
            (64, f"{directory}/{target_name}/64.json"),
        ]

        measurements = [(name, read_file(os.path.join(RESULT_DIR, file))) for (name, file) in files]

        lane_counts = np.array([name for name, _ in measurements])
        mcups = np.array([get_cups(measurement) / 1e6 for _, measurement in measurements]).T

        median = np.median(mcups, axis=0)
        speedup = median / sequential_cups[0]

        # CI errorbar
        res = stats.bootstrap((mcups,), np.median, confidence_level=0.99)
        lower_bound = (median - res.confidence_interval.low) / sequential_cups[0]
        upper_bound = (res.confidence_interval.high - median) / sequential_cups[0]
        yerr = np.vstack((lower_bound, upper_bound))

        ax.errorbar(lane_counts, speedup, yerr=yerr, fmt=plot_markers[target_name], capsize=3, color=plot_colors[target_name], label=target_name)

        # Fit Amdahl's law
        fit_until_index = list(lane_counts).index(LANE_COUNT) + 1

        normalized_mcups = median / median[0]
        popt, pcov = sp.optimize.curve_fit(amdahl, lane_counts[:fit_until_index], normalized_mcups[:fit_until_index])
        cont_lane_count = np.linspace(lane_counts[0], lane_counts[-1], 100000)
        ax.plot(cont_lane_count, amdahl(cont_lane_count, *popt) * median[0] / sequential_cups[0], ls="--", color=plot_colors[target_name])

        print("Amdahl's law fit", target_name, popt[0])

    # Set x-ticks and labels
    ax.set_xticks(lane_counts)
    labels = [str(lane_count) if lane_count != 2 else "" for lane_count in lane_counts]
    ax.set_xticklabels(labels)

    # Linear axis
    lim = ax.get_ylim()
    ax.plot([0, lane_counts[-1]], [0, lane_counts[-1]], ls="--", label="Linear scaling")
    ax.set_ylim(lim)

    # Add Amdahl's law label to legend
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Line2D([0], [0], color="black", ls='--', label="Amdahl's law fit"))
    ax.legend(handles=handles, loc='lower right')

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURE_DIR, f"lane_scaling_target_{directory}.pdf"))


def plot_lane_scaling_input(directory):
    sequential_result = read_file(os.path.join(RESULT_DIR, "sequential.json"))
    sequential_cups = get_cups(sequential_result) / 1e6
    fig = plt.figure()

    # Figure
    ax = fig.add_subplot(111)
    ax.set_xlabel("Lane count")
    ax.set_ylabel("MCUPS")
    ax.yaxis.set_minor_locator(MultipleLocator(1000))

    for target_name in ["disjoint", "random", "equal"]:
        files = [
            (1, f"{directory}/{target_name}/01.json"),
            (2, f"{directory}/{target_name}/02.json"),
            (4, f"{directory}/{target_name}/04.json"),
            (8, f"{directory}/{target_name}/08.json"),
            (16, f"{directory}/{target_name}/16.json"),
            (32, f"{directory}/{target_name}/32.json"),
            (64, f"{directory}/{target_name}/64.json"),
        ]

        measurements = [(name, read_file(os.path.join(RESULT_DIR, file))) for (name, file) in files]

        lane_counts = np.array([name for name, _ in measurements])
        mcups = np.array([get_cups(measurement) / 1e6 for _, measurement in measurements]).T

        print(len(lane_counts), len(mcups))
        median = np.median(mcups, axis=0)

        # Min/max errorbar
        # upper_bound = np.max(mcups, axis=0) - median
        # lower_bound = median - np.min(mcups, axis=0)
        # yerr = np.vstack((lower_bound, upper_bound))

        # CI errorbar
        res = stats.bootstrap((mcups,), np.median, confidence_level=0.99)
        lower_bound = median - res.confidence_interval.low
        upper_bound = res.confidence_interval.high - median
        yerr = np.vstack((lower_bound, upper_bound))

        ax.errorbar(lane_counts, median, yerr=yerr, fmt=".", capsize=3, label=target_name)
        # ax.errorbar(lane_counts, median, yerr=yerr, fmt=None, label=target_name)

    ax.axhline(np.median(sequential_cups), label="Sequential", ls="--", color="black")
    ax.set_xticks(lane_counts)
    labels = [str(lane_count) if lane_count != 2 else "" for lane_count in lane_counts]
    ax.set_xticklabels(labels)

    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURE_DIR, f"lane_scaling_target_{directory}.pdf"))

def plot_lane_scaling(directory, target_name):
    sequential_result = read_file(os.path.join(RESULT_DIR, "sequential.json"))
    sequential_cups = get_cups(sequential_result) / 1e6

    files = [
        (1, f"{directory}/{target_name}/01.json"),
        (2, f"{directory}/{target_name}/02.json"),
        (4, f"{directory}/{target_name}/04.json"),
        (8, f"{directory}/{target_name}/08.json"),
        (16, f"{directory}/{target_name}/16.json"),
        (32, f"{directory}/{target_name}/32.json"),
        (64, f"{directory}/{target_name}/64.json"),
    ]

    measurements = [(name, read_file(os.path.join(RESULT_DIR, file))) for (name, file) in files]

    lane_counts = np.array([name for name, _ in measurements])
    mcups = np.array([get_cups(measurement) / 1e6 for _, measurement in measurements]).T

    time_normalize_var = np.median(mcups[:, 0])
    mcups = mcups / time_normalize_var

    # Figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.boxplot(mcups, positions=lane_counts, notch=True, widths=3)
    ax.set_xticks(lane_counts)
    labels = [str(lane_count) if lane_count != 2 else "" for lane_count in lane_counts]
    ax.set_xticklabels(labels)
    ax.yaxis.set_minor_locator(MultipleLocator(1))

    ax.set_xlabel("Lane count")
    ax.set_ylabel("Speedup")

    # Amdahl's law
    popt, pcov = sp.optimize.curve_fit(amdahl, lane_counts[:-2], np.median(mcups, axis=0)[:-2])
    cont_lane_count = np.linspace(lane_counts[0], lane_counts[-3], 100000)
    ax.plot(cont_lane_count, amdahl(cont_lane_count, *popt), ls="--", label=f"Amdahls law fit: p={popt[0]:.2f}")
    print("Condition number", np.linalg.cond(pcov))
    print("RMS: ", np.sqrt(np.mean(np.power(amdahl(lane_counts[:-2], *popt) - np.median(mcups, axis=0)[:-2], 2))))


    # Amdahl's law
    popt, pcov = sp.optimize.curve_fit(amdahl, lane_counts, np.median(mcups, axis=0))
    cont_lane_count = np.linspace(lane_counts[0], lane_counts[-1], 100000)
    ax.plot(cont_lane_count, amdahl(cont_lane_count, *popt), ls="--", label=f"Amdahls law fit: p={popt[0]:.2f}")
    print("Condition number", np.linalg.cond(pcov))
    print("RMS: ", np.sqrt(np.mean(np.power(amdahl(lane_counts, *popt) - np.median(mcups, axis=0), 2))))

    # Linear axis
    lim = ax.get_ylim()
    ax.plot([0, lane_counts[-1]], [0, lane_counts[-1]], ls="--", label="Linear scaling")
    ax.set_ylim(lim)
    ax.axhline(np.median(sequential_cups)/time_normalize_var, label="Sequential", ls="--", color="black")


    # Second CUPS y-axis
    ax2 = ax.twinx()
    ax_min, ax_max = ax.get_ylim()
    ax2.set_ylim(ax_min * time_normalize_var, ax_max * time_normalize_var)
    ax2.set_ylabel("MCUPS")
    ax2.yaxis.set_minor_locator(MultipleLocator(1000))

    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURE_DIR, f"lane_scaling_{directory}_{target_name}.pdf"))

def plot_histogram(data):
    plt.hist(data["times"], bins = 100)
    res = stats.bootstrap((data["times"],), np.median, confidence_level=0.95)
    print(res.confidence_interval)
    mean = np.mean(data["times"])
    low = res.confidence_interval.low
    high = res.confidence_interval.high
    print(f"Mean: {mean}; Low: {low}; High: {high}")

    plt.axvline(low, color="red")
    plt.axvline(mean, color="purple")
    plt.axvline(high, color="red")

def get_cups(data):
    return data["query_size"] * data["target_size"] / np.array(data["times"]) * 1e9

def read_file(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        return data


if __name__ == '__main__':
    main()
