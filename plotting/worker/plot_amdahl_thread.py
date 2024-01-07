import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import json
import copy
import os

FIGURE_DIR = os.path.join(os.path.dirname(__file__), "../../figures/")

def amdahl(s, p):
    return 1 / ((1-p) + (p/s))

s1 = [1,2,4,8]
t_32 = [428.77, 227.159, 133.35, 127.06]
t_32_efficiency = [t_32[0] / t_32[i] / s1[i] * 100 for i in range(len(t_32))]
t_32_speedup = [t_32[0] / t_32[i] for i in range(len(t_32))]

t_16 = [217.56, 115.19, 66.82, 59.78]
t_16_efficiency = [t_16[0] / t_16[i] / s1[i] * 100 for i in range(len(t_16))]
t_16_speedup = [t_16[0] / t_16[i] for i in range(len(t_16))]

t_8 = [97.86, 52.79, 29.86, 25.70]
t_8_efficiency = [t_8[0] / t_8[i] / s1[i] * 100 for i in range(len(t_8))]
t_8_speedup = [t_8[0] / t_8[i] for i in range(len(t_8))]

t_L = [5.41, 2.96, 2.66, 2.73]
t_L_efficiency = [t_L[0] / t_L[i] / s1[i] * 100 for i in range(len(t_L))]
t_L_speedup = [t_L[0] / t_L[i] for i in range(len(t_L))]

t_rust_L = [4.98, 2.68, 1.84, 1.31]
t_rust_L_efficiency = [t_rust_L[0] / t_rust_L[i] / s1[i] * 100 for i in range(len(t_rust_L))]
t_rust_speedup = [t_rust_L[0] / t_rust_L[i] for i in range(len(t_rust_L))]

t_rust_XL = [167.00, 86.54, 48.82, 43.13]
t_rust_XL_efficiency = [t_rust_XL[0] / t_rust_XL[i] / s1[i] * 100 for i in range(len(t_rust_XL))]
t_rust_XL_speedup = [t_rust_XL[0] / t_rust_XL[i] for i in range(len(t_rust_XL))]

average_speedups = []
std_devs = []

for i in range(len(s1)):
    total_speedup = t_rust_XL_speedup[i] + t_rust_speedup[i] + t_8_speedup[i] + t_16_speedup[i] + t_32_speedup[i]
    average_speedup = total_speedup / 5  # Dividing by the number of datasets
    average_speedups.append(average_speedup)
    std_devs.append(np.std([t_rust_XL_speedup[i], t_rust_speedup[i], t_8_speedup[i], t_16_speedup[i], t_32_speedup[i]]))


plt.style.use([
    os.path.join(os.path.dirname(__file__), "../resources/vu.mplstyle"),
    os.path.join(os.path.dirname(__file__), "../resources/twocolumn.mplstyle"),
])

popt, pcov = scipy.optimize.curve_fit(amdahl, s1, average_speedups)
print("popt", popt, "pcov", pcov)


marker_size = 20

# with plt.style.context(["~/dev/latexclass/matplotlib/vu.mplstyle", "~/dev/latexclass/matplotlib/twocolumn.mplstyle"]):
colors = ['#0077B3', '#4FAF48', '#E8692D', '#8E4DA4', '#F2BA2F', '#D4CAC8', '#575756', '#003F6C']

plt.figure(figsize=(4, 3), dpi=600)

all_speedups = np.concatenate([t_rust_XL_speedup, t_rust_speedup, t_8_speedup, t_16_speedup, t_32_speedup])
buffer = 0.1 
lower_lim = max(min(all_speedups) - buffer, 0)  
upper_lim = max(all_speedups) + buffer





plt.scatter(s1, t_rust_XL_speedup, color=colors[2], s = marker_size, label="XL") # Or fmt="_" for a standard error bar.
plt.scatter(s1, t_rust_speedup, color=colors[3], s = marker_size, label="L") # Or fmt="_" for a standard error bar.
plt.scatter(s1, t_8_speedup, color=colors[4],  s = marker_size,label="Synthetic 8.000") # Or fmt="_" for a standard error bar.
plt.scatter(s1, t_16_speedup, color=colors[5], s = marker_size, label="Synthetic 16.000") # Or fmt="_" for a standard error ba
plt.scatter(s1, t_32_speedup, color=colors[6], s = marker_size, label="Synthetic 32.000") # Or fmt="_" for a standard error bar.

# plt.errorbar(s1, average_speedups, yerr=std_devs, color=colors[7], ls='none', 
#              fmt='D', markersize=2, markerfacecolor='none', markeredgewidth=1, 
#              capsize=5, label='Average Speedup w/ Std Dev', alpha=1)

n1 = np.linspace(s1[0], s1[-1], 100000)
plt.plot(n1, amdahl(n1, *popt), color=colors[1], ls="--", label=f"Amdahl's Law (p={round(popt[0], 2)})", alpha=1.0)

plt.plot([s1[0], s1[-1]], [s1[0], s1[-1]], color=colors[0], label="Linear Speed-up")
plt.legend(loc='upper left', fontsize = 6, )

plt.xlabel("Number of Cores")
plt.ylabel("Speed-up")
plt.xticks([2 ** i for i in range(4)])
plt.ylim(lower_lim, upper_lim)

plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, "strong_scalability_amdahls_threads.pdf"))
