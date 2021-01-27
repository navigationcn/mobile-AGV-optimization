import csv
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import random
import statistics as stat

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

    # construct some data like what you have:
    # x = np.random.randn(100, 8)
    # mins = x.min(0)
    # maxes = x.max(0)
    # means = x.mean(0)
    # std = x.std(0)
    #
    # # create stacked errorbars:
    # plt.errorbar(np.arange(8), means, std, fmt='ok', lw=3)
    # plt.errorbar(np.arange(8), means, [means - mins, maxes - means],
    #              fmt='.k', ecolor='gray', lw=1)
    # plt.xlim(-1, 8)
    # plt.show()
    # Plot results

    exp_name = "exp_50_2"

    horizon = np.array([0, 1, 2, 5, 10, 25, 50])
    improvement_1 = np.array([0, 8.32, 8.5, 9.75, 10.42, 12.27, 12.27])
    computation_max_1 = np.array([0, 0.418, 0.465, 0.643, 1.87, 38.67, 103.788])
    computation_avg_1 = np.array([0, 0.06, 0.12, 0.164, 0.267, 1.7, 3.59])
    computation_min_1 = np.array([0, 0.02, 0.06, 0.08, 0.12, 0.9, 1.65])

    horizon = horizon[:-2]
    improvement_1 = improvement_1[:-2]
    computation_max_1 = computation_max_1[:-2]
    computation_min_1 = computation_min_1[:-2]
    computation_avg_1 = computation_avg_1[:-2]

    mpl.style.use('default')
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('control horizon')
    ax1.set_ylabel('improvement [%]', color=color)
    ax1.plot(horizon, improvement_1, color=color, linestyle='None', marker='D')
    # color = 'tab:blue'
    # ax1.plot(horizon, improvement_2, color=color, linestyle='-', marker='*')
    ax1.tick_params(axis='y', labelcolor=color)
    # ax1.grid()

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'm'
    ax2.set_ylabel('computation time [s]', color=color)  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=color)
    # ax2.plot(horizon, computation_max, color=color, linestyle='None', marker='_')
    # ax2.plot(horizon, computation_avg, color='tab:cyan', linestyle='None', marker='_')
    ax2.errorbar(horizon, computation_avg_1, [computation_avg_1 - computation_min_1, computation_max_1 - computation_avg_1], fmt='_'+color, ecolor=color, lw=1, capsize=6, capthick=1)

    # color = 'm'
    # ax2.errorbar(horizon, computation_avg_2, [computation_avg_2 - computation_min_2, computation_max_2 - computation_avg_2], fmt='om', ecolor=color, lw=2, capsize=8, capthick=2)

    ax2.grid()
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    set_size(w=4, h=3)
    plt.subplots_adjust(left=0.16, bottom=0.18, right=0.80, top=None, wspace=None, hspace=None)
    plt.savefig("results/" + exp_name + "/" + exp_name + ".pdf", format="pdf", pad_inches=0.01, transparent=True)

    plt.show()

if __name__ == "__main__":
    main()
