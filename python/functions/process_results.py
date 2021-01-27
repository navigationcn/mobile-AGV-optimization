import csv
import yaml
import logging
import matplotlib.pyplot as plt
import numpy as np
import random
import statistics as stat
import os

logger = logging.getLogger(__name__)

def save_to_csv(solve_time, file_name):
    with open("results/" + file_name, mode='w') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(solve_time)

def read_csv_file(file_name):
    with open("results/" + file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            # logger.info(row)
            result = [float(i) for i in row]
        # logger.info(result)

    return result

def save_to_yaml(dict_results, file_name):
    pwd = os.path.dirname(os.path.abspath(__file__))
    with open(file_name, "w") as yaml_file:
        yaml.safe_dump(dict_results, yaml_file, default_flow_style=False)

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
    # TEST COLORS
    # h = 60
    # # colors = plt.cm.nipy_spectral( (np.arange(h)/h))
    # print(np.arange(h))
    # plt.figure()
    # for k in range(h):
    #     plt.scatter(random.uniform(0,1.0), random.uniform(0,1.0), color=colors[k])
    # plt.show()
    # return 0

    exp = "exp_50_2/"

    logger.info("showing results for {}".format(exp))
    fig, ax=plt.subplots()

    Horizon = ["1", "2", "5", "10", "25", "50", "75", "100", "200"]
    Horizon = ["1", "2", "5", "10", "25", "50"]
    colors = plt.cm.rainbow( np.arange(len(Horizon))/len(Horizon) )

    idx = 0
    Horizon.reverse()
    for H in Horizon:
        solve_time = read_csv_file(exp + "solve_time_H_" + H + ".csv")
        # logger.info(solve_time)
        plt.plot(solve_time, c=colors[idx], label=str(H))
        idx += 1

        logger.info("Computation time: H = {}".format(H))
        logger.info(" - max: {}".format(max(solve_time)))
        logger.info(" - avg: {}".format(stat.mean(solve_time)))

    plt.grid(True)
    plt.xlabel("time step [k]")
    plt.ylabel("Computation time [s]")
    plt.legend(title="control\nhorizon")
    plt.ylim([-0.1, 1.98])
    plt.xlim([-1.1, 100.1])

    # SET SIZING HERE!!
    set_size(w=3, h=3)
    plt.subplots_adjust(left=0.18, bottom=0.14, right=0.96, top=0.96, wspace=None, hspace=None)
    plt.savefig("results/" + exp + "comp_time_zoomin.pdf", format="pdf", pad_inches=0.01, transparent=True)

    plt.show()

if __name__ == "__main__":
    main()
