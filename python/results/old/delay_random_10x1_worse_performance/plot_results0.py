import csv
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import random
import statistics as stat
import glob
import os
import yaml

logger = logging.getLogger(__name__)

def set_size(w,h, ax=None):
    """ w, h: width, height in inches """
    if not ax: ax=plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    ax.figure.set_size_inches(figw, figh)

def main():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    yaml_list = glob.glob(dir_path + "/res_robots_*.yaml")

    dict_results = {}

    for file in yaml_list:
        split_filename = file.split("_")
        # print(split_filename)
        seed = str(split_filename[-1].split(".")[0])
        horizon = str(split_filename[-3])
        robots = str(split_filename[-5])
        try:
            print(dict_results[seed])
        except KeyError:
            dict_results[seed] = {}
        with open(file, "r") as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                cumulative_time = yaml_data["results"]["total time"]
                max_time = yaml_data["results"]["comp time"]["max"]
                avg_time = yaml_data["results"]["comp time"]["avg"]

                print("seed: {} horizon: {} robots: {} -> makespan: {}; max: {} avg: {}".format(seed, horizon, robots, cumulative_time, max_time, avg_time))

                dict_results[seed][horizon] = {}
                dict_results[seed][horizon]["robots"] = robots
                dict_results[seed][horizon]["cum_time"] = cumulative_time
                dict_results[seed][horizon]["max"] = max_time
                dict_results[seed][horizon]["avg"] = avg_time
            except yaml.YAMLError as exc:
                print(exc)

    print(dict_results)
    with open(dir_path + "/results.yaml", "w") as outfile:
        yaml.safe_dump(dict_results, outfile, default_flow_style=False)

    improv_list_1 = []
    comp_max_list_1 = []
    comp_avg_list_1 = []
    improv_list_5 = []
    comp_max_list_5 = []
    comp_avg_list_5 = []

    seed_list = []

    for exp in dict_results:
        try:
            # cumulative time results
            cost_0 = dict_results[exp]["0"]["cum_time"]
            cost_1 = dict_results[exp]["1"]["cum_time"]
            cost_5 = dict_results[exp]["5"]["cum_time"]
            improv_1 = round( 100*(int(cost_0)-int(cost_1))/int(cost_0) ,2)
            improv_5 = round( 100*(int(cost_0)-int(cost_5))/int(cost_0) ,2)
            improv_list_1.append(improv_1)
            improv_list_5.append(improv_5)

            # computation time results
            comp_max_1 = round(dict_results[exp]["1"]["max"], 3)
            comp_avg_1 = round(dict_results[exp]["1"]["avg"], 3)
            comp_max_5 = round(dict_results[exp]["5"]["max"], 3)
            comp_avg_5 = round(dict_results[exp]["5"]["avg"], 3)

            comp_max_list_1.append(comp_max_1)
            comp_avg_list_1.append(comp_avg_1)
            comp_max_list_5.append(comp_max_5)
            comp_avg_list_5.append(comp_avg_5)

            seed_list.append(int(exp))

            # print
            print("{} ->\t improv 1 {} ( {} | {} ) \t \t improv 5 {} ( {} | {} )".format(exp, improv_1, comp_avg_1, comp_max_1, improv_5, comp_avg_5, comp_max_5))

        except KeyError:
            pass

    print("avg improvement")
    print(" Horizon 1: {}".format(stat.mean(improv_list_1)))
    print(" Horizon 5: {}".format(stat.mean(improv_list_5)))
    print("avg comp. time [avg]")
    print(" Horizon 1: {}".format(stat.mean(comp_avg_list_1)))
    print(" Horizon 5: {}".format(stat.mean(comp_avg_list_5)))
    print("avg comp. time [max]")
    print(" Horizon 1: {}".format(stat.mean(comp_max_list_1)))
    print(" Horizon 5: {}".format(stat.mean(comp_max_list_5)))

    mpl.style.use('default')
    fig, ax1 = plt.subplots()

    seed_list.sort()

    color = 'tab:red'
    ax1.set_xlabel('Random seed')
    ax1.set_ylabel('Improvement [%]') #, color=color)
    ax1.plot(seed_list, improv_list_5, color="m", linestyle='-', marker='_', label="H = 5")
    ax1.plot(seed_list, improv_list_1, color="b", linestyle='-', marker='_', label="H = 1")
    ax1.plot(seed_list, [0]*len(seed_list), color="c", linestyle='-', marker='_', label="no MILP")
    ax1.grid()
    plt.legend(title="Horizon length")

    # color = 'tab:blue'
    # ax1.plot(horizon, improvement_2, color=color, linestyle='-', marker='*')
    ax1.tick_params(axis='y') #, labelcolor=color)
    # plt.ylim((-2, 20))set_size(w=4, h=3)
    set_size(w=4, h=3)
    plt.subplots_adjust(left=0.13, bottom=0.15, right=0.92, top=0.94, wspace=None, hspace=None)
    # plt.show()

    plt.savefig("./results/plots/10x1_improv.pdf", format="pdf", pad_inches=0.01, transparent=True)
    # plt.show()

    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Random seed')
    ax1.set_ylabel('Computation time [s]') #, color=color)
    color = 'm'
    ax1.errorbar(seed_list, comp_avg_list_5, [comp_avg_list_5, comp_max_list_5], fmt='_m', ecolor='m', lw=1, capsize=6, capthick=1, label="H = 5")
    ax1.errorbar(seed_list, comp_avg_list_1, [comp_avg_list_1, comp_max_list_1], fmt='_b', ecolor='b', lw=1, capsize=6, capthick=1, label="H = 1")
    ax1.grid()
    plt.legend(title="Horizon length")
    set_size(w=4, h=3)
    plt.subplots_adjust(left=0.13, bottom=0.15, right=0.92, top=0.94, wspace=None, hspace=None)
    plt.savefig("./results/plots/10x1_comptime.pdf", format="pdf", pad_inches=0.01, transparent=True)
    plt.show()

    return 0

if __name__ == "__main__":
    main()
