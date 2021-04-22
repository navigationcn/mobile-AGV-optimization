import csv
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import random
import statistics as stat
import plotly.graph_objects as go

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

    delay = [0,1,3,5,10,15]

    # Average improvement in percentage
    ct_70_1 = [0, 1.2,  1.7,  4.4,  6.7,  9.4]
    ct_60_2 = [0, 1.25, 2.0,  4.9,  7.1,  10.5]
    ct_50_1 = [0, 1.3,  2.2,  5.6,  7.9,  11.4]
    ct_40_1 = [0, 1.1,  2.6,  5.7,  8.2,  13.2]
    ct_30_1 = [0, 0.9,  1.9,  4.7,  7.4,  10.9]

    COUNT = 5
    colors = plt.cm.rainbow( np.arange(COUNT)/(COUNT-1))

    fig, ax = plt.subplots()
    ax.plot(delay[0:len(ct_70_1)], ct_70_1, color=colors[0], linestyle='--', marker='o', label="70")
    ax.plot(delay[0:len(ct_60_2)], ct_60_2, color=colors[1], linestyle='--', marker='o', label="60")
    ax.plot(delay[0:len(ct_50_1)], ct_50_1, color=colors[2], linestyle='--', marker='o', label="50")
    ax.plot(delay[0:len(ct_40_1)], ct_40_1, color=colors[3], linestyle='--', marker='o', label="40")
    ax.plot(delay[0:len(ct_30_1)], ct_30_1, color=colors[4], linestyle='--', marker='o', label="30")

    ax.grid()
    set_size(5,3,ax)
    plt.subplots_adjust(left=0.13, bottom=0.15, right=0.92, top=0.94, wspace=None, hspace=None)
    plt.legend(title="# AGVs")
    plt.xlabel("Delay length")
    plt.ylabel("Average Improvement [%]")
    plt.show()

if __name__ == "__main__":
    main()
