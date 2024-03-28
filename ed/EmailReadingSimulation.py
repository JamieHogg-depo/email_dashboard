import numpy as np
import matplotlib.pyplot as plt

class EmailReadingSimulation:
    def __init__(self, 
                 N_lower, N_upper, 
                 Rt_lower, Rt_upper,
                 At_lower, At_upper,
                 Wt_lower, Wt_upper,
                 Pr):
        # Assign all parameters to instance variables of the same name
        for name, value in locals().items():
            if name != 'self':
                setattr(self, name, value)
        
        # derived values
        self.Rt_guess = (Rt_upper - Rt_lower) / 2
        self.Rt_sd = (Rt_upper - Rt_lower) / 3.92  # Standard deviation calculation
        self.At_guess = (At_upper - At_lower) / 2
        self.At_sd = (At_upper - At_lower) / 3.92  # Standard deviation calculation
        self.Wt_guess = (Wt_upper - Wt_lower) / 2
        self.Wt_sd = (Wt_upper - Wt_lower) / 3.92  # Standard deviation calculation
        
        # initialise
        self.rt_total_vec = None
        self.at_total_vec = None
        self.wt_total_vec = None
        self.N_total_vec = None
        self.rt_total_sum = None
        self.at_total_sum = None
        self.wt_total_sum = None
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
    
    def num2Char2(self, x):
        """Convert numerical array to formatted string representation."""
        int95 = np.percentile(x, [2.5, 97.5])
        return "{} ({}, {})".format(int(np.median(x)), int(int95[0]), int(int95[1]))

    def simulate(self):
        """Simulate the distribution of total reading times."""
        rt_total = np.zeros(1000)
        at_total = np.zeros(1000)
        wt_total = np.zeros(1000)
        t_total = np.zeros(1000)
        N_total = np.zeros(1000)
        total_time_by_type = np.zeros([1000,3])
        total_time_by_type_relevant = np.zeros([1000,3])

        # run for 1000 iterations
        for s in range(1000):
        # for each iteration draw a set of reading, action and writing times for each type
        # doing this loop once is like a single dataset
            
            rt = np.empty(0) # array with size based on N_sim
            at = np.empty(0) # array with size based on N_sim
            wt = np.empty(0) # array with size based on N_sim
            N_sim = np.zeros(3, dtype=int) # number of emails of each type
            for i in range(3):

                # Draw number of emails
                N_sim[i] = np.random.randint(self.N_lower[i], self.N_upper[i]+1, 1)
               
                # simulate whether each email is relevant or not
                binary_relevant = np.random.binomial(1, self.Pr[i], N_sim[i])
                
                 # simulate reading, action and writing times
                rt = self.gammaDraw(self.Rt_guess[i], self.Rt_sd[i], N_sim[i])
                at = self.gammaDraw(self.At_guess[i], self.At_sd[i], N_sim[i])
                wt = self.gammaDraw(self.Wt_guess[i], self.Wt_sd[i], N_sim[i])

                # Derive total time by type
                # add to matrix
                total_time_by_type[s,i] = rt.sum()+at.sum()+wt.sum()
                total_time_by_type_relevant[s,i] = np.sum( (rt + at + wt) * binary_relevant)

                # add other types to initial vectors
                rt = np.append(rt, self.gammaDraw(self.Rt_guess[i], self.Rt_sd[i], N_sim[i]))
                at = np.append(at, self.gammaDraw(self.At_guess[i], self.At_sd[i], N_sim[i]))
                wt = np.append(wt, self.gammaDraw(self.Wt_guess[i], self.Wt_sd[i], N_sim[i]))
                # rt, at and wt are discarded each iteration of t
            rt_total[s] = rt.sum()
            at_total[s] = at.sum()
            wt_total[s] = wt.sum()
            t_total[s] = rt_total[s] + at_total[s] + wt_total[s]
            N_total[s] = N_sim.sum()

        # assign as attributes
        self.rt_total_vec = rt_total
        self.at_total_vec = at_total
        self.wt_total_vec = wt_total
        self.t_total_vec = t_total
        self.N_total_vec = N_total
        self.total_time_by_type = total_time_by_type
        self.median_total_type = np.median(total_time_by_type, axis=0)
        self.median_total_type_relevant = np.median(total_time_by_type_relevant, axis=0)

        # format output
        self.rt_total_sum = self.num2Char(self.rt_total_vec)
        self.wt_total_sum = self.num2Char(self.at_total_vec)
        self.at_total_sum = self.num2Char(self.wt_total_vec)
        self.t_total_sum = self.num2Char(self.t_total_vec)
        self.N_total_sum = self.num2Char2(self.N_total_vec)