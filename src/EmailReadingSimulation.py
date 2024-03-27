# Created by ChatGPT

import numpy as np
import matplotlib.pyplot as plt

class EmailReadingSimulation:
    def __init__(self, N_lower, N_upper, point, lower, upper):
        self.N_lower = N_lower
        self.N_upper = N_upper
        self.point = point # minutes
        self.lower = lower
        self.upper = upper
        self.sd_input = (upper - lower) / 3.92  # Standard deviation calculation
        # initialise
        self.rt_total_vec = None
        self.N_total_vec = None
        self.rt_total_sum = None
        self.N_total_sum = None

    def gammaDraw(self, mu, sigma, n):
        """Draw samples from a gamma distribution."""
        k = mu ** 2 / sigma ** 2
        theta = sigma ** 2 / mu
        return np.random.gamma(k, theta, n)

    def num2Char(self, x):
        """Convert numerical array to formatted string representation."""
        int95 = np.percentile(x, [2.5, 97.5])
        return "{:.2f} ({:.2f}, {:.2f})".format(np.median(x), int95[0], int95[1])

    def simulate(self):
        """Simulate the distribution of total reading times."""
        rt_total = np.zeros(1000)
        N_total = np.zeros(1000)
        for t in range(1000):
            rt = np.empty(0)
            N_sim = np.zeros(3, dtype=int)
            for i in range(3):
                N_sim[i] = np.random.randint(self.N_lower[i], self.N_upper[i], 1)
                rt = np.append(rt, self.gammaDraw(self.point[i], self.sd_input[i], N_sim[i]))
            rt_total[t] = rt.sum()
            N_total[t] = N_sim.sum()

        self.rt_total_vec = rt_total
        self.N_total_vec = N_total
        self.rt_total_sum = self.num2Char(self.rt_total_vec)
        self.N_total_sum = self.num2Char(self.N_total_vec)

    def plot(self, rt_total):
        """Plot histogram of total reading times."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(rt_total, bins=30, density=True, alpha=0.6, color='g')
        return fig, ax

# Example usage
simulation = EmailReadingSimulation(N_lower=np.array([15, 30, 28]),
                                    N_upper=np.array([16, 31, 29]),
                                    point=np.array([8, 3.33, 1.25]),
                                    lower=np.array([7.9, 3.3, 1.2]),
                                    upper=np.array([8.1, 3.4, 1.3]))

# update attributes
simulation.simulate()
# view summaries
simulation.rt_total_sum; simulation.N_total_sum

# show histogram plot
fig, ax = simulation.plot(rt_total)
fig.show()  # Display the plot
