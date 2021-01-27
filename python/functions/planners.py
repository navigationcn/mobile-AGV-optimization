"""
    Interface with executable global planners such as CBS, ECBS etc.
"""

import subprocess
import yaml
import os
import logging

import networkx as nx
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def run_ECBS_TA(map_file, robot_file, w=1.2):
    logger.info("running ECBS TA ...")
    subprocess.run(
        ["../build/ecbs_ta",
    	 "-m", map_file,
         "-r", robot_file,
    	 "-w", str(w),
    	 "-o", "data/tmp/output.yaml"],
    	check=True)
    logger.info("done!")
    with open("data/tmp/output.yaml") as output_file:
        return yaml.safe_load(output_file)

def run_ECBS(map_file, robot_file, w, thread_number=1):
    logger.info("running ECBS ...")
    tmp = "tmp" + str(thread_number)
    subprocess.run(
        ["../build/ecbs",
         "-m", map_file,
         "-r", robot_file,
         "-w", str(w),
         "-o", "data/" + tmp + "/output.yaml"],
        check=True)
    logger.info("done!")
    with open("data/"  + tmp + "/output.yaml") as output_file:
        return yaml.safe_load(output_file)

def run_CBS(map_file, robot_file, w=1.0, thread_number=1):
    if float(w) != 1.0:
        return run_ECBS(map_file, robot_file, w, thread_number=thread_number)
    else:
        tmp = "tmp" + str(thread_number)
        subprocess.run(
            ["../build/cbs",
        	 "-m", map_file,
             "-r", robot_file,
        	 "-o", "data/" + tmp + "/output.yaml"],
        	check=True)
        with open("data/" + tmp + "/output.yaml") as output_file:
            return yaml.safe_load(output_file)
