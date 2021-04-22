import csv
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import random
import seaborn as sns
import pandas as pd
import statistics as stat
import os
import glob
import yaml
import plotly.graph_objects as go

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(name)s - %(levelname)s :: %(message)s', level=logging.INFO)

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

    sns.set(style="darkgrid")
    data = {"AGVs": [], "randseed": [], "delay": [], "horizon": [], "total_time": [], "improvement": []}

    # import data
    dir_path = os.path.dirname(os.path.realpath(__file__))
    yaml_list = glob.glob(dir_path + "/ICAPS/*.yaml")

    horizon_0_data = {"AGVs": [], "randseed": [], "delay": [], "total_time": []}

    for file in yaml_list:
        split_filename = file.split("_")
        horizon = str(split_filename[-1].split(".")[0])
        delay = str(split_filename[-3])
        seed = str(split_filename[-5])
        AGVs = str(split_filename[-7])
        logger.info("AGVs: {} \t Seed: {} \t Delay: {} \t Horizon: {}".format(AGVs, seed, delay, horizon))
        with open(file, "r") as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                cumulative_time = yaml_data["results"]["total time"]

                data["AGVs"].append(int(AGVs))
                data["randseed"].append(int(seed))
                data["delay"].append(int(delay))
                data["horizon"].append(int(horizon))
                data["total_time"].append(int(cumulative_time))
                data["improvement"].append(int(cumulative_time))

            except yaml.YAMLError as exc:
                print(exc)

    # Calculate the improvement percentage
    # for df in data:

    df = pd.DataFrame(data, columns=["AGVs", "randseed", "delay", "horizon", "total_time", "improvement"])
    print(df)

    df_0 = df[df.horizon == 0]
    print(df_0)

    newdata = {"AGVs": [], "randseed": [], "delay": [], "horizon": [], "total_time": [], "improvement": []}

    for index, row in df.iterrows():
        AGVs = row["AGVs"]
        randseed = row["randseed"]
        delay = row["delay"]
        horizon = row["horizon"]
        total_time = row["total_time"]

        baseline = df_0[(df_0.AGVs == AGVs) & (df_0.randseed == randseed) & (df_0.delay == delay)].iloc[0]

        baseline_time = baseline["total_time"]
        improvement = 100*(baseline_time-total_time)/baseline_time
        logger.info(improvement)

        newdata["AGVs"].append(int(AGVs))
        newdata["randseed"].append(int(seed))
        newdata["delay"].append(int(delay))
        newdata["horizon"].append(int(horizon))
        newdata["total_time"].append(int(cumulative_time))
        newdata["improvement"].append(int(improvement))

    dfnew = pd.DataFrame(newdata, columns=["AGVs", "randseed", "delay", "horizon", "total_time", "improvement"])
    print(dfnew)

    dfnew_horizon1 = dfnew[dfnew.horizon == 1]
    dfnew_horizon2 = dfnew[dfnew.horizon == 2]
    dfnew_horizon3 = dfnew[dfnew.horizon == 3]
    dfnew_horizon4 = dfnew[dfnew.horizon == 4]
    dfnew_horizon5 = dfnew[dfnew.horizon == 5]

    # Plot the responses for different events and regions
    plt.figure(1)
    sns.lineplot(x="delay", y="improvement",
                 hue="AGVs",
                 data=dfnew_horizon1)
    plt.title("Horizon = {}".format(1))

    # plt.figure(2)
    # sns.lineplot(x="delay", y="improvement",
    #              hue="AGVs",
    #              data=dfnew_horizon2)
    # plt.title("Horizon = {}".format(2))
    #
    # plt.figure(3)
    # sns.lineplot(x="delay", y="improvement",
    #              hue="AGVs",
    #              data=dfnew_horizon3)
    # plt.title("Horizon = {}".format(3))
    #
    # plt.figure(4)
    # sns.lineplot(x="delay", y="improvement",
    #              hue="AGVs",
    #              data=dfnew_horizon4)
    # plt.title("Horizon = {}".format(4))
    #
    # plt.figure(5)
    # sns.lineplot(x="delay", y="improvement",
    #              hue="AGVs",
    #              data=dfnew_horizon5)
    # plt.title("Horizon = {}".format(5))

    plt.show()

if __name__ == "__main__":
    main()
