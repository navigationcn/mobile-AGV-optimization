"""
    Determine the Action Dependency Graph of ECBS determined plans
"""

import sys
import yaml
import time
import matplotlib.colors as mcolors
import matplotlib
import random
import time
import numpy as np
import subprocess
sys.path.insert(1, "functions/")

def main():
    thread_number = 5
    # An automated script to run multiple scenarios

    # SIMULATION
    # thread 1: islands 50
    # thread 2: islands 30, 40
    # thread 3: islands 60
    # thread 4: islands 70

    # DONE:
    # islands   30, 40 ,50, 60, 70
    # general   50, 30, 40
    # halfgen   50, 30, 40
    # nuernberg 50, 30, 40

    # nuernberg, islands
    
    # map_name = "nuernberg"
    # for map_name in ["nuernberg", "islands", "general", "halfgen"]

    for seedvaliter in [16,17,18,19,20]: #[6,7,8,9,10]: #[1,2,3,4,5]: #[16,17,18,19,20]: #[11,12,13,14,15]: #[6,7,8,9,10]: #[1,2,3,4,5]:
            # 
        seedval = seedvaliter + 20
        for map_name in ["nuernberg", "halfgen", "islands", "nuernberg"]:

            for robots in [50]: # number of AGVs
                # Generate new map
                subprocess.run(
                    ["python",
                    "data/generate_map.py",
                    str(robots), 
                    str(seedval), 
                    str(thread_number),
                    map_name],            # DEFINE THE MAP NAME
                    check=True)
                # Run the optimization on this new map
                for delay in [10]:
                    for horizon in [0,5]:
                        solver = "CBC"
                        for cost_func_name in ["cumulative"]: #, "cumulative", "binary_penalty", "greedy"]:
                            subprocess.run(
                                ["python",
                                    "main_ECBS.py",
                                    str(robots),
                                    str(seedval),
                                    str(horizon),
                                    str(delay),
                                    str(thread_number),
                                    solver,
                                    "thesis/dif_maps/" + map_name,
                                    map_name,
                                    cost_func_name],
                                check=True)

if __name__ == "__main__":
    main()
