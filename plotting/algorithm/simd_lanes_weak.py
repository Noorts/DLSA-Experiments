import matplotlib.pyplot as plt
import numpy as np
import scipy

plt.rcParams["font.family"] = "Source Sans Pro"

def amdahl(s, p):
    return 1 / ((1-p) + (p/s))
    # return 1/ (1 - p)


def main():
    lane_counts = np.array([1, 2, 4, 8, 16, 32, 64])
    lb = np.array([441.80, 518.47, 702.54, 847.11, 898.65, 954.92, 944.01])
    estimate = np.array([442.81, 529.41, 707.78, 850.58, 905.63, 966.09, 946.67])
    ub = np.array([443.71, 539.56, 712.37, 853.62, 911.51, 975.63, 949.10])

    lane_counts = lane_counts[:-1]
    lb = lb[:-1]
    estimate = estimate[:-1]
    ub = ub[:-1]

    estimate_normalized = estimate / estimate[0]

    y_error = np.empty((2, len(lane_counts)))

    y_error[0, :] = estimate - lb
    y_error[1, :] = ub - estimate

    y_error_normalized = y_error / estimate[0]

    popt, pcov = scipy.optimize.curve_fit(amdahl, lane_counts, estimate_normalized)
    cont_lane_count = np.linspace(lane_counts[0], lane_counts[-1], 100000)


    fig = plt.figure()
    with plt.style.context(["../resources/twocolumn.mplstyle", "../resources/vu.mplstyle"]):
        ax = fig.add_subplot(111)
        ax.errorbar(lane_counts, estimate_normalized, yerr=y_error_normalized, fmt='o', capsize=5, label="Measurements")
        ax.plot(cont_lane_count, amdahl(cont_lane_count, *popt), ls="--", label=f"Amdahls law fit: p={popt[0]:.2f}")
        ax.set_xticks(lane_counts)
        ax.set_xlabel("Lane count")
        ax.set_ylabel("Speedup")

        ax2 = ax.twinx()
        ax_min, ax_max = ax.get_ylim()
        ax2.set_ylim(ax_min*estimate[0], ax_max*estimate[0])
        ax2.set_ylabel('CUPS')
        ax.legend()
        plt.tight_layout()

        plt.show()


if __name__ == '__main__':
    main()
