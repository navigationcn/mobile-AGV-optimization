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

    horizon = [1,2,5,10,25,50,75,100,200]

    # maximum computation times
    ct_67_1 = [0.664, 1.053, 1.887]
    ct_67_2 = [0.644, 1.221, 1.964, 5.811]
    ct_60_2 = [0.653, 0.951, 1.577]
    ct_50_1 = [0.325, 0.338, 0.987, 1.398, 11.17, 54.95]
    ct_50_2 = [0.418, 0.465, 0.643, 1.87, 38.67, 103.788]
    ct_40_1 = [0.39, 0.488, 0.82, 1.26, 4.61]
    ct_40_2 = [0.292, 0.516, 0.54, 1.12, 4.57, 17.87]
    ct_30_1 = [0.071, 0.0806, 0.184, 0.341, 0.447, 0.609, 0.65, 0.622]
    ct_30_2 = [0.065, 0.11, 0.14, 0.255, 0.595, 1.148]
    COUNT = 5

    colors = plt.cm.rainbow( np.arange(COUNT)/(COUNT-1) )
    fig, ax =plt.subplots()

    ax.plot(horizon[0:len(ct_67_1)], ct_67_1, color=colors[0], linestyle='--', marker='o', label="70")
    ax.plot(horizon[0:len(ct_60_2)], ct_60_2, color=colors[1], linestyle='--', marker='o', label="60")
    ax.plot(horizon[0:len(ct_50_1)], ct_50_1, color=colors[2], linestyle='--', marker='o', label="50")
    ax.plot(horizon[0:len(ct_40_1)], ct_40_1, color=colors[3], linestyle='--', marker='o', label="40")
    ax.plot(horizon[0:len(ct_30_1)], ct_30_1, color=colors[4], linestyle='--', marker='o', label="30")

    ax.grid()
    plt.legend(title="# AGVs")
    set_size(w=5,h=3,ax=ax)
    plt.xlabel("Horizon length")
    plt.ylabel("Peak computation time [s]")
    plt.show()

if __name__ == "__main__":
    main()
