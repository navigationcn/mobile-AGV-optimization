"""
    File to visualize the output of planning schemes
"""

import json
import yaml
import numpy as np
import matplotlib
# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter

import logging
logger = logging.getLogger(__name__)

class Visualizer(object):
    def __init__(self, map_file, robots):
        self.map_file = map_file
        self.robots = robots
        self._read_map_file()
        self.fig = plt.figure()
        self.redraw(robots)


    def _read_map_file(self):
        with open(self.map_file) as stream:
            try:
                map_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.warning(exc)
                map_data = None

        dim = map_data["map"]["dimensions"]
        map_array = np.zeros(dim)
        for obstacle in map_data["map"]["obstacles"]:
            x = obstacle[0]
            y = obstacle[1]
            map_array[x, y] = 1.0

        # add padding for plotting
        map_array = np.pad(map_array,(1,1),mode="constant",constant_values=1.0)

        self.map_array = map_array


    def redraw(self, robots, pause_length=1.0, show_traj=False, writer=None):
        plt.clf()
        plt.imshow(self.map_array, cmap="pink")
        show_goals = True
        for alpha in np.linspace(0,1,6):
            for robot in self.robots:
                color = robot.get_color()
                pos = robot.get_position()
                if robot.advance_this_step:
                    pos_prev = robot.get_prev_position()
                    if alpha == 1.0:
                        robot.advance_this_step = False
                else:
                    pos_prev = pos

                # logger.info("color: {} pos: {}".format(color, pos))
                pos_y = alpha*pos["y"] + (1-alpha)*pos_prev["y"]
                pos_x = alpha*pos["x"] + (1-alpha)*pos_prev["x"]

                plt.scatter(pos_y+1, pos_x+1, c=color, marker="o") # add +1 for plotting

                if show_goals:
                    goal_y = robot.goal_position["y"]
                    goal_x = robot.goal_position["x"]
                    plt.scatter(goal_y+1, goal_x+1, s=80, facecolors='none', edgecolors=color) #c=color, marker="x")

            if show_traj:
                for robot in self.robots:
                    if robot.robot_ID in [0,4,11,13]:
                        path = robot.plan_positions
                        x_vec = []
                        y_vec = []
                        for node in path:
                            y_vec.append(node["x"]+1)
                            x_vec.append(node["y"]+1)
                        y_vec.append(robot.goal_position["x"]+1)
                        x_vec.append(robot.goal_position["y"]+1)
                        # logger.info("x_vec: {}".format(x_vec))
                        # logger.info("y_vec: {}".format(y_vec))
                        # logger.info("color: {}".format(robot.color))
                        plt.plot(x_vec, y_vec, color=robot.color[0])

            plt.pause(0.001)
            if writer is not None:
                writer.grab_frame()
            plt.clf()
            plt.imshow(self.map_array, cmap="pink")

    



def show_factory_map(map_file, robot_file, show=False):
    """
        Shows graph of simple CBS or ECBS input files.
        NOT FOR TA algorithms
    """
    with open(map_file) as stream:
        try:
            map = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.warning(exc)
            map = None

    with open(robot_file) as stream:
        try:
            robot_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.warning(exc)
            robot_data = None

    dim = map["map"]["dimensions"]
    map_array = np.zeros(dim)
    for obstacle in map["map"]["obstacles"]:
        x = obstacle[0]
        y = obstacle[1]
        map_array[x, y] = 1.0

    robot_count = 0
    for robot in robot_data["robots"]:
        robot_count += 1
        # logger.info(robot)
        xs = int(robot["start"][0])
        ys = int(robot["start"][1])
        xg = int(robot["goal"][0])
        yg = int(robot["goal"][1])
        map_array[xs, ys] = 6.0
        map_array[xg, yg] = 6.0

    fig = plt.figure()
    # plt.title("Factory map")

    ax = plt.gca()
    # ax.set_xlim([ ])
    # ax.set_ylim([ ])
    print(ax)

    map_to_plot = np.pad(map_array,(1,1),mode="constant",constant_values=1.0)
    plt.imshow(map_to_plot)
    plt.xlabel("y")
    plt.ylabel("x")
    if show:
        plt.show()

    return map_array, robot_count
