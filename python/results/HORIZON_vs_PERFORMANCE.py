import csv
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import random
import statistics as stat
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

"""
    HORIZON AFFECT ON IMPROVEMENT [%] PLOT
"""

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

    horizon = [0,1,2,5,10,15,50,75,100,200]

    # maximum computation times
    ct_67_1 = [0,8,10,12,12]
    ct_60_2 = [0,9,11,12,11.8]
    ct_50_1 = [0,7.6,12.2,13.1,13.1]
    ct_40_1 = [0,5.1,6.1,6.7,7.1,8.5]
    ct_30_1 = [0,3.5,5.4,5.5,5.1,6.3]
    COUNT = 5

    colors = plt.cm.rainbow( np.arange(COUNT)/(COUNT-1) )
    fig, ax =plt.subplots()

    ax.plot(horizon[0:len(ct_67_1)], ct_67_1, color=colors[0], linestyle='--', marker='o', label="70")
    ax.plot(horizon[0:len(ct_60_2)], ct_60_2, color=colors[1], linestyle='--', marker='o', label="60")
    ax.plot(horizon[0:len(ct_50_1)], ct_50_1, color=colors[2], linestyle='--', marker='o', label="50")
    ax.plot(horizon[0:len(ct_40_1)], ct_40_1, color=colors[3], linestyle='--', marker='o', label="40")
    ax.plot(horizon[0:len(ct_30_1)], ct_30_1, color=colors[4], linestyle='--', marker='o', label="30")

    ax.grid()
    set_size(w=5,h=3,ax=ax)
    plt.legend(title="# AGVs",loc="bottom right")
    plt.xlabel("Horizon length")
    plt.ylabel("Avg Improvement [%]")
    plt.show()

if __name__ == "__main__":
    main()
