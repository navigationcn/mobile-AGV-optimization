# Mobile AGV Optimization

Based on the paper [A Feedback Scheme to Reorder a Multi-Agent Execution Schedule by Persistently Optimizing a Switchable Action Dependency Graph](https://arxiv.org/abs/2010.05254)
by A. Berndt, N. van Duijkeren, L. Palmieri and T. Keviczky

## Get Started

Execute the following commands to compile and run this repo. 


1. Clone the repository

```
cd ~/
git clone https://github.com/alexberndt/mobile-AGV-optimization.git
cd ~/mobile-AGV-optimization/
```

2. Build and compile the ECBS MAPF planner
```
cd ~/mobile-AGV-optimization/
mkdir build
cd build
cmake ..
make
```
Look at the output when running *cmake* to ensure you have all the dependencies installed. Known dependencies include:

- *doxygen* 
  ```
  apt-get install doxygen
  ```
 
- *yaml-cpp*
  ```
  apt-get install libyaml-cpp-dev
  ```
  
Check the output of *cmake* to verify all dependencies are installed, and then run *make*.

3. Setup the python environment to run the SADG algorithms

If you use conda, simply create a new conda environment 
```
conda create --name sadg_env python=3.6
conda activate sadg_env
```
Then install the python dependencies using *pip*
```
pip3 install -r requirements.txt
```

## Overview of python files

### python/main_ECBS.py

This file runs the SADG algorithm. 

If run using *main.py*, the parameters used are in lines 60-78,
If run standalone, the input parameters are lines 38-56.


### python/main.py

The main file setup to test various maps, AGV fleet sizes, solvers, horizon lengths, delays etc.

This code runs the */data/generate_map.py* and */main_ECBS.py* files to create a map,
and run the SADG algorithm respectively.

### ./data/generate_map.py

Generates a random map and task file based on an AGV group size and map csv file.

### ./data/

Directory which holds various map definitions in csv format.
Each map has a number-suffix when running multiple instances of the algorithm on different threads.

csv_map.csv: a map defined by a 2D array, where 0 = free space, 1 = goal locations, 9 = obstacle. The goal locations are used in generate_map.py to randomly assign AGVs to goal locations.

csv_robots_yaml.yaml and csv_map_yaml.yaml are automatically generated by ./data/generate_map.py based on csv_map.csv

## Simple Example

Consider the following illustrative example:

Goal: define a map for 40 AGVs, and generate random goals and run the SADG algorithm. 

Assuming the installation has been performed as detailed above, the steps are:

1. Generate the map and task files by running ./data/generate_map.py 

    First change robot count to 40 (line 23) and the map name to "/general1" (line 26). For different random positions, change the random seed (line 24) 
```
    python generate_map.py

```
2.  Run the SADG algorithm using main_ECBS.py

    since we directly run main_ECBS.py (as opposed to running main.py which itself runs main_ECBS.py), the parameters we need to change at in lines 39-56.

    To show the moving robots, set show_visual to True, show_ADG to False (ADGs for large groups of AGVs > 40) take a lot of time to plot, run_MILP to True to perform switching.

    Set the H_control to 2, the control horizon, and delay_amount to 10, and delayed_robot_cnt = 14, meaning 14 of the AGVs will be randomly selected and delayed every 10th time-step.

```
    python main_ECBS.py
```

## Important to Note

The ECBS code is obtained from https://github.com/whoenig/libMultiRobotPlanning

However, it has been adapted to accommodate for a different input arguments used by this Python framework. The input files are now split into a *mapfile* and a *taskfile*, instead of a single *inputfile* containing both the map and task data, as in the original code by whoenig.
