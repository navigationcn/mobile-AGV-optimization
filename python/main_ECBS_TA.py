"""
    baseline ECBS-TA for reactive analysis
    includes Task Assignment
"""

import sys
import yaml
import time
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import random


sys.path.insert(1, "functions/")
from planners import *
from visualizers import *
from robot_obj import Robot

def main():

    # import files
    map_file = "data/manual_00/map.yaml"
    robot_TA_file = "data/manual_00/robots_ta.yaml"
    robot_TA_file_tmp = "data/tmp/robots_ta.yaml"    
    plans = run_ECBS_TA(map_file, robot_TA_file, w=1.2)

    for robot, plan in plans.items():
        print(robot)

    # return 0

    # show graph
    area_mat, robot_count = show_graph(map_file, robot_TA_file, False)
    plt.axis([-1, 15, -1, 19])
    plt.imshow(area_mat.transpose())
    cmap = plt.get_cmap('hsv') # choose from print(matplotlib.cm.cmap_d.keys())
    colors = cmap(np.linspace(0.0, 1.0, robot_count))

    # init robots
    robots = []
    idx = 0
    for agent, plan in plans["schedule"].items():
        x = plan[0]["x"]
        y = plan[0]["y"]
        # plot_obj, = ax.scatter(x,y)
        color = [colors[idx]]
        idx += 1

        new_robot = Robot(agent, plan, None, color)
        robots.append(new_robot)

    # run receding horizon
    for t in range(20):
        print(t)
        plans_must_change = False

        plt.clf()
        plt.axis([-1, 15, -1, 19])
        plt.imshow(area_mat.transpose())

        robot_dict = {}
        robot_dict["robots"] = []
        # for robot, plan in plans["schedule"].items():
        for robot in robots:

            # check if robot reached goal
            if len(robot.path) == 1:
                print("{} has finished!".format(robot.name))
                x = robot.path[0]["x"]
                y = robot.path[0]["y"]
                input_dict = {"name": robot.name, "start": [str(x), str(y)], "goal": [str(x), str(y)]}
                robot_dict["robots"].append(input_dict)
            # if robot not yet at goal
            elif len(robot.path) > 1:

                cur_x = robot.x
                cur_y = robot.y
                next_x = robot.path[1]["x"]
                next_y = robot.path[1]["y"]
                node_x = next_x
                node_y = next_y

                new_x = next_x #cur_x + random.uniform(0.6,0.9)*(next_x - cur_x)
                new_y = next_y #cur_y + random.uniform(0.6,0.9)*(next_y - cur_y)

                xg = robot.path[-1]["x"]
                yg = robot.path[-1]["y"]

                on_schedule = robot.update_loc((new_x, new_y))
                if not on_schedule:
                    plans_must_change = True
                    node_x = robot.path[0]["x"]
                    node_y = robot.path[0]["y"]
                # update path in-case required
                input_dict = {"name": robot.name, "start": [str(node_x), str(node_y)], "goal": [str(xg), str(yg)]}
                robot_dict["robots"].append(input_dict)
            else:
                print("<< aN eRRoRrR hAs oCuRRrRrReD >>")
            plt.scatter(robot.x, robot.y, c=robot.color)

        if plans_must_change:
            print("Ein robot haz disobeyed ze commands! rE-OptImIzE zE PlAnS!")
            with open(robot_file_tmp, "w") as robot_file:
                yaml.safe_dump(robot_dict, robot_file, sort_keys=True, default_flow_style=False)
            plans = run_CBS(map_file, robot_file_tmp)
            print(" --> runtime: {}".format(plans["statistics"]["runtime"]))
        else:
            print("no plans changed: no re-calculation required")
        plt.pause(0.5)

    plt.show()

if __name__ == "__main__":
    main()
