#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
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

RESULT_DIR = os.path.join(os.path.dirname(__file__), "../../PC/")
FIGURE_DIR = os.path.join(os.path.dirname(__file__), "../../figures/")

def main():
    if len(sys.argv) > 1:
        print("Using result directory", sys.argv[1])
        global RESULT_DIR
        RESULT_DIR = sys.argv[1]
    else:
        print("No result directory provided, assuming", RESULT_DIR)

    plot_target_scalability()

    plt.show()

def plot_target_scalability():
    fig = plt.figure(figsize=(4, 4))

    # Figure
    ax = fig.add_subplot(111)
    ax.set_xlabel("Target size")
    ax.set_ylabel("MCUPS")
    ax.yaxis.set_minor_locator(MultipleLocator(1000))

    target_sizes = [2**i for i in range(10, 21)]

    platforms = os.listdir(RESULT_DIR)
    print(platforms)

    for platform in platforms:
        files = [ (target_size, f"{platform}/{target_size}.json") for target_size in target_sizes]

        measurements = [(target_size, read_file(os.path.join(RESULT_DIR, file))) for (target_size, file) in files]

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

        ax.errorbar(target_sizes, median, yerr=yerr, fmt=".", capsize=3, label=platform)
        # ax.errorbar(lane_counts, median, yerr=yerr, fmt=None, label=target_name)

    ax.set_xscale("log")
    ax.set_xticks(target_sizes[::2], minor=False)
    ax.set_xticklabels(target_sizes[::2], minor=False)
    ax.set_xticks(target_sizes, minor=True)
    ax.set_xticklabels([], minor=True)

    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURE_DIR, "target_scalability.pdf"))

def get_cups(data):
    return data["query_size"] * data["target_size"] / np.array(data["times"]) * 1e9

def read_file(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        return data


if __name__ == '__main__':
    main()
