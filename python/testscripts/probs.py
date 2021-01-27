import numpy as np
import matplotlib.pyplot as plt

"""
    PLOTS PROBABILITY DISTRIBUTION FUNCTIONS
"""

def main():
    vals = []
    mu = 0.3
    np.random.seed(1)
    vals = np.random.poisson(mu, size=1000)
    print(vals)
    hist_vals = np.histogram(vals, bins=np.arange(0,100))
    print(hist_vals)

    plt.figure()
    plt.hist(vals, bins=np.arange(0,100), density=True)
    plt.show()

if __name__ == "__main__":
    main()
