"""
    Iterative MILP solved to determine optimal ordering defined by ADG
"""

import sys
import yaml
import time
import matplotlib.colors as mcolors
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
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

    # a simulation that runs a CBS algorithm and executes without the ADG
    """ --------------------------- INPUTS --------------------------------- """
    show_visual = True
    show_ADG = False #not show_visual
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
    delayed_robot_cnt = 10

    w = 1.4                # sub-optimality bound: w = 1.0 -> CBS, else ECBS!
    fldr = "presentation"  # auto_gen_01_nuernberg | auto_gen_00_large | auto_gen_02_simple | manual_03_maxplus

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

    robot_plan, goal_positions = determine_robot_plans(plans, show_graph=False)

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

    # for robot_plan_i in robot_plan:
    #     logger.info(robot_plan_i)
    #     logger.info(robot_plan[robot_plan_i]["positions"])

    metadata = dict(title='Movie Test', artist='Matplotlib',
            comment='Movie support!')
    writer = FFMpegWriter(fps=10, metadata=metadata)

    with writer.saving(visualizer.fig, "writer_test.mp4", 500):

        for i in np.arange(0,35): #35):
            logger.info(i)
            for robot in robots:
                # logger.info("{} : {}".format(robot.robot_ID, robot.get_position()))
                # logger.info("   plan: {}".format(robot.plan_positions))
                # logger.info("   current node: {}".format(robot.current_idx))
                plans_sequence = robot.plan_positions
                this_robot_goal_pos = plans_sequence[min(robot.current_idx+1, robot.plan_length-1)]
                # logger.info("   next position to go to: {}".format(this_robot_goal_pos))
                # first check if the space ahead is occupied
                cannot_advance = False
                for other_robot in robots:
                    other_robot_pos = other_robot.get_position()
                    # logger.info("other: {}, this: {}".format(other_robot_pos, this_robot_goal_pos))
                    if other_robot_pos == this_robot_goal_pos:
                        cannot_advance = True
                proba_val = random.uniform(0,1)
                bound_prob = 1.995
                if (not cannot_advance and proba_val < bound_prob):
                    robot.advance()
                else:
                    continue
                    # logger.info("CANNOT ADVANCE!!!!")
                # logger.info("{} : {}".format(robot.robot_ID, robot.current_position))
            # if i == 0:
            #     visualizer.show_trajectories(robots)

            if show_visual:
                visualizer.redraw(robots, pause_length=0.001, show_traj=True, writer=writer)



if __name__ == "__main__":
    main()
