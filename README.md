# utility
The repository contains various utility scripts to do small but useful things.

Pre-requisites

Python

`pip install pandas matplotlib`

[monitory.py](monitor.py) - This script allows you to capture `dstat` in specified intervals for any bash or python script.

Example usage: 

`python monitor.py <interval> <output_file> <script_path> [<arg1> <arg2> ... <argN>]`


[plot_dstat.py](plot_dstat.py) - This script plots the CPU utilization and Memory utilization when a dsat output file is provided as an input

Example usage: 

`python plot_dstat.py <dstat_file> <path to cpu_image> <path to memory_image>`
