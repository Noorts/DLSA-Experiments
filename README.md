# Alignment@Home Experiment Results

## Introduction

This repository is an archive for the [Alignment@Home](https://github.com/Noorts/DLSA) project's experiments (for more information about the project see the project repository's README file). Specifically, it contains both 1) experiment setups and results, and 2) plotting code and the generated plots.

## Details

### DAS5

In the DAS5 directory, subdirectories can be found that contain:

1. A `result_....json` JSON (which is parsed by the plotting code).
2. An `...-extrainfo.txt` file which contains the experimental setup and if relevant the settings used to produce synthetic queries.
3. SLURM output files from both the master and worker nodes. System utilization metrics can be found in the `...-sys.out` files.

### Plotting

Contains the code used to create the plots contained in the report.
