"""
	READ CSV TO CREATE MAP AND ROBOT YAML FILES

	Reads a map CSV file ("csv_map_file") and creates:
	1) MAP FILE: "yaml_map_file" which contains a 4-cell connect
	2) ROBOTS FILE: "robot_yaml_file" which contains robots with
	   randomized start and goal positions
"""
import csv
import yaml
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import argparse
import os
import sys

def main():

	# INPUTS:
	separate_start_and_goal = False		# If true, goals only at 2's, starts at 1 in csv file
	robot_count = 50					# number of robots to add to plan
	seedval = 0							#
	pwd = os.path.dirname(os.path.abspath(__file__))
	base_loc = pwd + "/nuernberg1"		#  auto_gen_00_large | auto_gen_01_nuernberg | auto_gen_02_simple
	csv_map_file = base_loc + "/csv_map.csv"				# location of csv file of graph
	yaml_map_file = base_loc + "/csv_map_yaml.yaml"
	robot_yaml_file = base_loc + "/csv_robots_yaml.yaml"
	trigger = True

	print("Running map generator ...")
	try:
		robot_count = int(sys.argv[1])
		seedval = int(sys.argv[2])
		map_name = str(sys.argv[4])
		base_loc = pwd + "/" + map_name + str(sys.argv[3])		#  auto_gen_00_large | auto_gen_01_nuernberg | auto_gen_02_simple
		csv_map_file = base_loc + "/csv_map.csv"				# location of csv file of graph
		yaml_map_file = base_loc + "/csv_map_yaml.yaml"
		robot_yaml_file = base_loc + "/csv_robots_yaml.yaml"
		if robot_count < 2 or seedval < 1:
			raise ValueError
		print("  Inputs accepted!  ")
	except ValueError:
		print("  Inputs were not integers such that:")
		print("    robot_count > 2")
		print("    seedval > 0")
	except:
		print("  No arguments given... using in-script values")
	finally:
		print("  Using the following parameters for map generation:")
		print("    robot_count: {}".format(robot_count))
		print("    seedval: {}".format(seedval))

	random.seed(seedval)

	# Read csv file
	# 0 = free block, 1/2 = start/goal position, 9 = obstacle
	file = pd.read_csv(csv_map_file)
	map_array = file.values
	dim = map_array.shape

	map_array_plot = np.power(map_array, 0.3)
	const_val = np.power([9], 0.3)
	map_array_plot = np.pad(map_array_plot,(1,1),mode="constant",constant_values=const_val[0])
	# plt.imshow(map_array_plot, cmap="pink") # bone, afmhot
	# plt.show()

	### --------------------- MAP FILE ----------------------------
	# Init map fictionary for YAML file structure
	map_dict = {}
	map_dict["map"] = {}
	map_dict["map"]["dimensions"] = [dim[0], dim[1]]
	map_dict["map"]["obstacles"] = []
	start_locs = []
	goal_locs = []

	for row_idx in range(dim[0]):
		for col_idx in range(dim[1]):
			cell_val = map_array[row_idx][col_idx]
			if separate_start_and_goal:
				if cell_val == 1:
					start_locs.append((row_idx, col_idx))
				if cell_val == 2:
					goal_locs.append((row_idx, col_idx))
				# trigger = not trigger
			else:
				if cell_val == 1 or cell_val == 2:
					start_locs.append((row_idx, col_idx))
					goal_locs.append((row_idx, col_idx))
			if cell_val == 9:
				map_dict["map"]["obstacles"].append([row_idx, col_idx])

	print("  len(goal_locs): {}".format(len(goal_locs)))
	print("  len(start_locs): {}".format(len(start_locs)))

	# Write to YAML file
	with open(yaml_map_file, "w") as map_file:
		yaml.safe_dump(map_dict, map_file, sort_keys=True, default_flow_style=False)

	### --------------------- ROBOTS FILE ----------------------------
	# create robots with randomly assigned start and goal locations
	robot_dict = {}
	robot_dict["robots"] = []

	for id in range(robot_count):
		robot_start = (0,0)
		robot_goal = (0,0)
		while robot_start == robot_goal:
			# random start location
			startlist_len = len(start_locs)
			random_start_idx = random.randint(0, startlist_len-1)
			robot_start = start_locs[random_start_idx]

			# random goal location
			goallist_len = len(goal_locs)
			random_goal_idx = random.randint(0, goallist_len-1)
			robot_goal = goal_locs[random_goal_idx]

		robot_start = start_locs.pop(random_start_idx)
		robot_goal = goal_locs.pop(random_goal_idx)

		# add to dictionary object
		input_dict = {"name": "boi" + str(id), "start": [robot_start[0], robot_start[1]], "goal": [robot_goal[0], robot_goal[1]]}
		robot_dict["robots"].append(input_dict)

	# write to YAML file
	with open(robot_yaml_file, "w") as robot_file:
		yaml.safe_dump(robot_dict, robot_file, sort_keys=True, default_flow_style=False)

	print("done!")

if __name__ == "__main__":
	main()
