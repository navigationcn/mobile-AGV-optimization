"""
	Determines the ADG graph and reverse ADG graph for plan inputs
	Also includes dependency groups
"""

import networkx as nx
import matplotlib.pyplot as plt
import logging
import time

from functions.adg_node import *
from functions.adg_dependency_group import *

logger = logging.getLogger(__name__)

def draw_ADG(ADG, robots, graph_title="ADG graph", writer=None):
	# plt.title(graph_title)

	# get current robot node to adjust positions
	position_offset = {}
	for robot in robots:
		current_node_position = int(robot.current_node.split("_")[2])
		position_offset[robot.robot_ID] = current_node_position

	# update positions (move finished nodes backwards)
	pos = nx.get_node_attributes(ADG, "pos")
	for node, plot_pos in pos.items():
		robot_id_of_node = int(node.split("_")[1])
		new_plot_pos = (plot_pos[0]-position_offset[robot_id_of_node], plot_pos[1])
		pos[node] = new_plot_pos # update position for plotting

	nodelist = []
	nodecolor = []
	for node in ADG.nodes(data=True):
		nodelist.append(node[0])
		if node[1]["data"].status == Status.STAGED:
			nodecolor.append("r")
		elif node[1]["data"].status == Status.FINISHED:
			nodecolor.append("g")
		else: # ENQUEUED!
			nodecolor.append("y")
	labels_dict = None # nx.get_node_attributes(ADG, "label")
	nx.draw_networkx(ADG, pos=pos, node_color=nodecolor, labels=labels_dict, with_labels=False)

	plt.xlim(-20,20)

	if writer is not None:
		writer.grab_frame()
	plt.clf()

def determine_ADG(plans, show_graph=False, show_logging=False):
	"""
		Based on the global robot plans determined by a global planning
		algorithm (e.g. CBS, CCBS, ECBS, ..), determine the action dependency
		graph (ADG)
		Inputs:
		 - plans
		Outputs:
		 - ADG : action dependency graph
		 - robot_plan : dictionary of robot plans
		 - goal_positions : dictionary of robot goal positions => only plotting!
	"""

	logger.info("Determining ADG")
	start = time.process_time()

	for robot, plan in plans["schedule"].items():
		logger.debug("  {} :{}".format(robot,plan))
	logger.info(" Constructing ADG from plans ...")
	ADG = nx.DiGraph()

	# create robot plan for simulation (required later on)
	robot_plan = {}

	goal_positions = {}

	# ADD NODES AND TYPE 1 EDGES
	robot_ID = 0
	# loop through each robot's plan
	logger.info("  1 adding nodes and type 1 edges ...")
	for robot, plan in plans["schedule"].items():
		# robot plan
		robot_plan[robot_ID] = {}
		robot_plan[robot_ID]["nodes"] = []
		robot_plan[robot_ID]["positions"] = []

		goal_positions[robot_ID] = plan[-1]

		plan_length = len(plan)
		node_idx = 0
		for idx, item in enumerate(plan[:-1]): # loop through all elements, BUT last
			next_item = plan[idx+1]
			if not (item["x"] == next_item["x"] and item["y"] == next_item["y"]): # check for difference in position
				node_ID = "p_" + str(robot_ID) + "_" + str(node_idx)
				robot_plan[robot_ID]["nodes"].append(node_ID)
				robot_plan[robot_ID]["positions"].append({"x": item["x"], "y": item["y"]})
				ADG_node = ADGNode(node_ID, item, next_item)
				ADG.add_node(node_ID, data=ADG_node, pos=(item["t"], robot_ID), label=ADG_node.info)
				if node_idx > 0: # Add edge if a node has been added
					prev_node_ID = "p_" + str(robot_ID) + "_" + str(node_idx-1)
					ADG.add_edge(prev_node_ID, node_ID, type=1)
				node_idx += 1

		# if start and goal are the same
		if plan_length == 1:
			item = plan[0]
			node_ID = "p_" + str(robot_ID) + "_" + str(node_idx)
			ADG_node = ADGNode(node_ID, item, item)
			ADG.add_node(node_ID, data=ADG_node, pos=(item["t"], robot_ID), label=ADG_node.info)

		# next robot ID
		robot_ID += 1
	logger.debug("    done!")

	robot_count = robot_ID
	robot_ID_list = range(robot_count)

	# ADD TYPE 2 EDGES
	logger.info("  2 adding type 2 edges ...")
	for this_robot_ID in robot_ID_list:
		this_node_idx = 0
		this_node_ID = "p_" + str(this_robot_ID) + "_" + str(this_node_idx)
		this_neighbor_list = list(ADG.neighbors(this_node_ID))
		while len(this_neighbor_list) > 0: # while list not empty
			this_node = ADG.nodes[this_node_ID]["data"]
			for other_robot_ID in robot_ID_list:
				if other_robot_ID != this_robot_ID:
					other_node_idx = 0
					other_node_ID = "p_" + str(other_robot_ID) + "_" + str(other_node_idx)
					other_neighbor_list = list(ADG.neighbors(other_node_ID))

					while len(other_neighbor_list) > 0:
						other_node = ADG.nodes[other_node_ID]["data"]
						if (this_node.s_loc == other_node.g_loc) and (this_node.time <= other_node.time):
							ADG.add_edge(this_node_ID, other_node_ID, type=2)
						other_node_idx += 1
						other_node_ID = "p_" + str(other_robot_ID) + "_" + str(other_node_idx)
						other_neighbor_list = list(ADG.neighbors(other_node_ID))

			# get next node in list
			this_node_idx += 1
			this_node_ID = "p_" + str(this_robot_ID) + "_" + str(this_node_idx)
			this_neighbor_list = list(ADG.neighbors(this_node_ID))
	logger.debug("    done!")
	logger.info("  done! ADG construction took {} s".format(time.process_time() - start))

	if show_graph:
		plt.figure()
		plt.title("Original ADG graph")
		pos = nx.get_node_attributes(ADG, "pos")
		labels_dict = nx.get_node_attributes(ADG, "label")
		nx.draw_networkx(ADG, pos=pos, labels=labels_dict, with_labels=True)
		# plt.show()

	return ADG, robot_plan, goal_positions

def analyze_ADG(G_ADG, plans, show_graph=False):
	"""
		Inputs:
		 - Action dependency graph G_ADG
		 - plans of each robot
		Outputs:
		 - all ADG nodes
		 - all type 1 edges
		 - dependency groups
	"""

	logger.info(" Analyzing ADG to get switchable dependencies")
	start = time.process_time()

	all_edges = G_ADG.edges()
	logger.debug("   all edges: {}".format(all_edges))

	edges_type_1 = [(u,v) for u,v,e in G_ADG.edges(data=True) if e["type"] == 1]
	logger.debug("   Type 1: {}".format(edges_type_1))

	edges_type_2 = [(u,v) for u,v,e in G_ADG.edges(data=True) if e["type"] == 2]
	logger.debug("   Type 2: {}".format(edges_type_2))

	edges_type_2_orig = edges_type_2.copy()
	# remove edges part of group

	dependency_groups = []

	logger.debug(len(edges_type_2))
	for edge in edges_type_2_orig:
		added_to_existing_group = False
		for group in dependency_groups:
			logger.debug("currently checking edge {}".format(edge))
			logger.debug(group.type)
			if group.next_edge_same(edge):
				logger.debug("same found")
				added_to_existing_group = True
				break
			elif group.next_edge_opposite(edge):
				added_to_existing_group = True
				break

		if not added_to_existing_group:
			logger.debug("creating new group for edge: {}".format(edge))
			new_group = DependencyGroup(edge)
			dependency_groups.append(new_group)

		logger.debug(edge)

	for group in dependency_groups:
		logger.debug("group (type: {}): {} ".format(group.type, group.edges))
		group.determine_reverse()

	rev_edges = []

	group_count = 0
	for group in dependency_groups:
		logger.debug("rev group: {}".format(group.reverse_edges))
		group_count += 1
		for edge in group.reverse_edges:
			rev_edges.append(edge)

	logger.info("  Depenency groups: {}".format(group_count))

	# obtain reverse groups:
	G_new_ADG = nx.DiGraph()
	pos = nx.get_node_attributes(G_ADG, "pos")
	G_new_ADG.add_nodes_from(G_ADG.nodes())
	G_new_ADG.add_edges_from(edges_type_1)
	G_new_ADG.add_edges_from(rev_edges)

	logger.info("  done! ADG analysis took {} s".format(time.process_time() - start))

	if show_graph:
		plt.figure()
		plt.title("Reversed dependency ADG graph")
		pos = nx.get_node_attributes(G_ADG, "pos")
		labels_dict = nx.get_node_attributes(G_ADG, "label")
		nx.draw_networkx(G_new_ADG, pos=pos, with_labels=True, labels=labels_dict)
		# plt.show()

	adg_nodes_all = G_ADG.nodes()

	return adg_nodes_all, edges_type_1, dependency_groups

def determine_robot_plans(plans, show_graph=False, show_logging=False):
	"""
		Based on the global robot plans determined by a global planning
		algorithm (e.g. CBS, CCBS, ECBS, ..), determine the robot plans. This is
		ONLY for the deadlock simulation!
		Inputs:
		 - plans
		Outputs:
		 - robot_plan : dictionary of robot plans
		 - goal_positions : dictionary of robot goal positions => only plotting!
	"""

	logger.info("Determining robot plans (with possible deadlocks)")
	start = time.process_time()

	for robot, plan in plans["schedule"].items():
		logger.debug("  {} :{}".format(robot,plan))
	logger.info(" Constructing ADG from plans ...")
	ADG = nx.DiGraph()

	# create robot plan for simulation (required later on)
	robot_plan = {}

	goal_positions = {}

	# ADD NODES AND TYPE 1 EDGES
	robot_ID = 0
	# loop through each robot's plan
	logger.info("  1 adding nodes and type 1 edges ...")
	for robot, plan in plans["schedule"].items():
		# robot plan
		robot_plan[robot_ID] = {}
		robot_plan[robot_ID]["nodes"] = []
		robot_plan[robot_ID]["positions"] = []

		goal_positions[robot_ID] = plan[-1]

		plan_length = len(plan)
		node_idx = 0
		for idx, item in enumerate(plan[:-1]): # loop through all elements, BUT last
			next_item = plan[idx+1]
			if not (item["x"] == next_item["x"] and item["y"] == next_item["y"]): # check for difference in position
				logger.info("same nodes are NOT merged in ADG for deadlock simulation!")
			node_ID = "p_" + str(robot_ID) + "_" + str(node_idx)
			robot_plan[robot_ID]["nodes"].append(node_ID)
			robot_plan[robot_ID]["positions"].append({"x": item["x"], "y": item["y"]})
			ADG_node = ADGNode(node_ID, item, next_item)
			ADG.add_node(node_ID, data=ADG_node, pos=(item["t"], robot_ID), label=ADG_node.info)
			if node_idx > 0: # Add edge if a node has been added
				prev_node_ID = "p_" + str(robot_ID) + "_" + str(node_idx-1)
				ADG.add_edge(prev_node_ID, node_ID, type=1)
			node_idx += 1

		# if start and goal are the same
		if plan_length == 1:
			item = plan[0]
			node_ID = "p_" + str(robot_ID) + "_" + str(node_idx)
			ADG_node = ADGNode(node_ID, item, item)
			ADG.add_node(node_ID, data=ADG_node, pos=(item["t"], robot_ID), label=ADG_node.info)

		# next robot ID
		robot_ID += 1
	logger.debug("    done!")

	robot_count = robot_ID
	robot_ID_list = range(robot_count)

	return robot_plan, goal_positions
