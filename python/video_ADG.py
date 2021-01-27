"""
    closed-loop MILP solved to determine optimal ordering defined by ADG
"""

import sys
import yaml
import time
import matplotlib.colors as mcolors
import matplotlib
import matplotlib.pyplot as plt
import random
import logging
import time
import networkx as nx
import csv
import statistics as stat
import os
import sys
from mip import Model, ProgressLog, xsum, maximize, minimize, BINARY, CONTINUOUS, Constr, ConstrList

sys.path.insert(1, "functions/")
from planners import *
from visualizers import *
from milp_formulation import *
from robot import *
from adg import *
from adg_node import *
from process_results import *

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(name)s - %(levelname)s :: %(message)s', level=logging.INFO)

def main():

    """ --------------------------- INPUTS --------------------------------- """
    show_visual = False
    show_ADG = True #not show_visual
    run_MILP = True #False #True
    save_file = False
    sim_timeout = 500

    # define prediction and control horizons: H_prediction >= H_control
    H_prediction = np.NaN # integer value for forward node lookup
    H_control = 5
    random_seed = 0
    mu = 0.5
    robust_param = 0.0
    delay_amount = 5
    delayed_robot_cnt = 2

    w = 1.4                # sub-optimality bound: w = 1.0 -> CBS, else ECBS!
    fldr = "nuernberg_small"  # auto_gen_01_nuernberg | auto_gen_00_large | auto_gen_02_simple | manual_03_maxplus

    random.seed(random_seed)
    np.random.seed(random_seed)
    """ -------------------------------------------------------------------- """

    # start initial
    pwd = os.path.dirname(os.path.abspath(__file__))
    logger.info(pwd)
    map_file = pwd + "/data/" + fldr + "/csv_map_yaml.yaml"
    robot_file = pwd + "/data/" + fldr + "/csv_robots_yaml.yaml"
    robot_file_tmp = pwd + "/data/tmp/robots.yaml"
    start_time = time.time()
    plans = run_CBS(map_file, robot_file, w=w) # if w > 1.0, run_CBS uses ECBS!
    logger.info(" with sub-optimality w={}".format(w))
    logger.info(" plan statistics: {} \n".format(plans["statistics"]))
    logger.debug(plans["schedule"])

    # show factory map
    # show_factory_map(map_file, robot_file, True)
    # plt.show()

    map_gen_robot_count = 10
    map_gen_seedval = "NaN"
    try:
        map_gen_robot_count = int(sys.argv[1])
        map_gen_seedval = int(sys.argv[2])
        H_control = int(sys.argv[3])
        robust_param = int(sys.argv[4])
        random.seed(map_gen_seedval) # map_gen_seedval
        np.random.seed(map_gen_seedval) # map_gen_seedval
    except:
        print(" no valid inputs given, ignoring ...")

    # determine ADG, reverse ADG and dependency groups
    ADG, robot_plan, goal_positions = determine_ADG(plans, show_graph=False)
    nodes_all, edges_type_1, dependency_groups = analyze_ADG(ADG, plans, show_graph=False)
    ADG_reverse = ADG.reverse(copy=False)

    # initialize simulation
    robots = []
    solve_time = []
    robots_done = []
    time_to_goal = {}
    colors = plt.cm.rainbow( np.arange(len(robot_plan))/len(robot_plan) )
    for robot_id in robot_plan:
        plan = robot_plan[robot_id]
        logger.debug("Robot {} - plan: {} \t \t positions: {}".format(robot_id, plan["nodes"], plan["positions"]))
        new_robot = Robot(robot_id, plan, colors[robot_id], goal_positions[robot_id])
        robots.append(new_robot)
        robots_done.append(False)
        time_to_goal[robot_id] = 0

    if show_visual:
        visualizer = Visualizer(map_file, robots)

    # initialize optimization MIP object m_opt
    m_opt = Model('MILP_sequence', solver='CBC')
    # print(m_opt.max_nodes)
    pl_opt = ProgressLog()
    # pl_opt.settings = "objective_value"
    # print("pl_opt.settings: {}".format(pl_opt.settings))
    # print("pl_opt.log: {}".format(pl_opt.log))
    # pl_opt.instance = m_opt.name
    # print("pl_opt.instance: {}".format(pl_opt.instance))

    ADG_fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    metadata = dict(title='Movie Test', artist='Matplotlib',
            comment='Movie support!')
    writer = FFMpegWriter(fps=2, metadata=metadata)

    with writer.saving(ADG_fig, "ADG_video.mp4", 500):
        # run a simulation in time
        k = 0
        robot_IDs_to_delay = []
        while (not all(robots_done)) and (k < sim_timeout):
            print("pl_opt.log: {}".format(pl_opt.log))
            m_opt.clear()

            # show current robot status
            logger.info("-------------------- @ time step k = {} --------------------".format(k))
            for robot in robots:
                node_info = ADG.node[robot.current_node]["data"]
                logger.debug("   - Robot {} # {} @ {} => status: {}".format(robot.robot_ID, node_info.ID, node_info.s_loc, robot.status))

            # solve MILP for the advanced ADG to potentially adjust ordering
            res, solve_t = solve_MILP(robots, dependency_groups, ADG, ADG_reverse, H_control, H_prediction, m_opt, pl_opt, run=run_MILP, uncertainty_bound=robust_param)
            solve_time.append(solve_t)
            if not (res is None or res == "OptimizationStatus.OPTIMAL"):
                ValueError("Optimization NOT optimal")

            # ADG after MILP
            if show_ADG:
                #
                draw_ADG(ADG, robots, "ADG after MILP ADG | k = {}".format(k), writer=writer)
                # plt.show()

            # check for cycles
            try:
                nx.find_cycle(ADG, orientation="original")
                logger.warning("Cycle detected!!")
                raise Exception("ADG has a cycle => deadlock! something is wrong with optimization")
            except nx.NetworkXNoCycle:
                logger.debug("no cycle detected in ADG => no deadlock. good!")
                pass


            if (k % delay_amount) == 0:
                robot_IDs = np.arange(map_gen_robot_count)
                robot_IDs_to_delay = np.random.choice(map_gen_robot_count, size=delayed_robot_cnt, replace=False)
                logger.info("delaying robots (ID): {}".format(robot_IDs_to_delay))

            # Advance robots if possible (dependencies have been met)
            for robot in robots:
                # check if all dependencies have been met, to advance to next node
                node_info = ADG.node[robot.current_node]["data"]
                node_dependencies_list = list(ADG_reverse.neighbors(robot.current_node))
                all_dependencies_completed = True
                for dependency in node_dependencies_list:
                    if (ADG.node[dependency]["data"].status != Status.FINISHED):
                        all_dependencies_completed = False

                # if all dependencies are completed, the robot can advance!

                # delay_amount = np.random.poisson(mu) # same sample every time

                if all_dependencies_completed and k > 0: # (robot.robot_ID == 2 or k > 5)
                    if (not (robot.robot_ID in robot_IDs_to_delay)): # or (k < 10 or k > 20)): # or (robot.robot_ID == 3 or k > 8):
                        ADG.node[robot.current_node]["data"].status = Status.FINISHED
                        robot.advance()

                if not robot.is_done():
                    time_to_goal[robot.robot_ID] += 1
                else:
                    robots_done[robot.robot_ID] = True

            if show_visual:
                visualizer.redraw(robots, pause_length=0.1)
                # return 0

            k += 1
        # end of while loop


    total_time = 0
    for idx, t in time_to_goal.items():
        total_time += t

    logger.info("Total time to complete missions: {}".format(total_time))
    logger.info("horizon = {}".format(H_control))
    logger.info("")
    logger.info("Computation time:")
    logger.info(" - max: {}".format(max(solve_time)))
    logger.info(" - avg: {}".format(stat.mean(solve_time)))

    # create data to save to YAML file
    simulation_results = {}
    simulation_results["parameters"] = {}
    simulation_results["parameters"]["H_control"] = H_control
    simulation_results["parameters"]["random seed"] = random_seed
    simulation_results["parameters"]["ECBS w"] = w
    simulation_results["parameters"]["mu"] = mu
    simulation_results["parameters"]["robust param"] = robust_param
    simulation_results["parameters"]["delay amount"] = delay_amount
    simulation_results["map details"] = {}
    simulation_results["map details"]["robot_count"] = map_gen_robot_count
    simulation_results["map details"]["seed val"] = map_gen_seedval
    simulation_results["results"] = {}
    simulation_results["results"]["comp time"] = {}
    simulation_results["results"]["comp time"]["solve_time"] = [solve_time]
    simulation_results["results"]["comp time"]["max"] = max(solve_time)
    simulation_results["results"]["comp time"]["avg"] = stat.mean(solve_time)
    simulation_results["results"]["total time"] = total_time

    logger.info(simulation_results)
    file_name = pwd + "/results/robust_" +str(delayed_robot_cnt) + "x" + str(delay_amount) + "/res_robots_" + str(map_gen_robot_count) +  "_horizon_" + str(H_control) + "_mapseed_" + str(map_gen_seedval) + "_robustparam_" + str(robust_param) + ".yaml"
    if save_file:
        save_to_yaml(simulation_results, file_name)

if __name__ == "__main__":
    main()
