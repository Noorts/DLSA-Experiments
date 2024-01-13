# DLSA Experiment Results

## Introduction

This repository is an archive for the [DLSA](https://github.com/Noorts/DLSA) project's experiments (for more information about the project see the project repository's README file). Specifically, it contains both 1) experiment setups and results, and 2) plotting code and the generated plots.

## Contents

| Category     | Experiments | Directories     |
|--------------|-------------|-----------------|
| System-level | Exp. 1, 2   | DAS5            |
| Worker-level | Exp. 3, 4   | plotting/worker |
| Algorithm    | Exp. 5, 6   | EC2, PC         |
| Competition  |             | Competition     |

## Details

### DAS5

In the DAS5 directory, subdirectories can be found that contain:

1. A `result_....json` JSON (which is parsed by the plotting code).
2. An `...-extrainfo.txt` file which contains the experimental setup and if relevant the settings used to produce synthetic queries. The `Commit ID` details the version of the Alignment@Home project that was used during the experiment.
3. SLURM output files from both the master and worker nodes. System utilization metrics can be found in the `...-sys.out` files.

Note: the `elapsed_time` and `computation_time` measurements are stored in the result files in **milliseconds**.

### Competition

The Competition directory contains results produced for the class competition. This directory in addition to the contents mentioned in the DAS5 section above, also has a subdirectory with the sequence alignment results. Note that for these results the top-k parameter was set to 5, and due to the CLI's result processing multiple runs have appended to the same file (thus there are more than 5 results in the file).

### Plotting

Contains the code used to create the plots contained in the report.

---

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/Noorts/DLSA-Experiments">Distributed Local Sequence Alignment — Experiment (artifacts)</a> by <span property="cc:attributionName">Haraldur Davíðsson, Paul Groß, Niclas Haderer, Simon van Noort, Daniël Voogsgerd, and Enrico Zeilmaker</span> is marked with <a href="http://creativecommons.org/publicdomain/zero/1.0?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC0 1.0 Universal<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/zero.svg?ref=chooser-v1"></a></p>
