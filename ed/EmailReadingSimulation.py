import numpy as np
import matplotlib.pyplot as plt

class EmailReadingSimulation:
    def __init__(self, 
                TeamSize,
                Pay,
                Period,
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
        self.Rt_guess = (Rt_upper + Rt_lower) / 2
        self.Rt_sd = (Rt_upper - Rt_lower) / 3.92  # Standard deviation calculation
        self.At_guess = (At_upper + At_lower) / 2
        self.At_sd = (At_upper - At_lower) / 3.92  # Standard deviation calculation
        self.Wt_guess = (Wt_upper + Wt_lower) / 2
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
        return "{:.1f} ({:.1f} - {:.1f})".format(np.median(x), int95[0], int95[1])
    
    def num2Char2(self, x):
        """Convert numerical array to formatted string representation."""
        int95 = np.percentile(x, [2.5, 97.5])
        return "{} ({} - {})".format(int(np.median(x)), int(int95[0]), int(int95[1]))
    
    def num2Char_dollars(self, x):
        """Convert numerical array to formatted string representation."""
        int95 = np.percentile(x, [2.5, 97.5])
        return "${:,.0f} (${:,.0f} - ${:,.0f})".format(np.median(x), int95[0], int95[1])

    def simulate(self):
        """Simulate the distribution of total reading times."""
        rt_total = np.zeros(1000)
        at_total = np.zeros(1000)
        wt_total = np.zeros(1000)
        t_total_vec = np.zeros(1000)
        t_essential_vec = np.zeros(1000)
        t_nonessential_vec = np.zeros(1000)
        N_total_vec = np.zeros(1000)
        total_time_by_type = np.zeros([1000,3])
        total_time_by_type_essential = np.zeros([1000,3])
        total_time_by_type_nonessential = np.zeros([1000,3])

        # run for 1000 iterations
        for s in range(1000):
        # for each iteration draw a set of reading, action and writing times for each type
        # doing this loop once is like a single dataset
            
            # create list of lists to store vectors of times for each type
            rt_all_types = [[], [], []]
            at_all_types = [[], [], []]
            wt_all_types = [[], [], []]

            # initilise number of emails of each type
            N_sim = np.zeros(3, dtype=int)

            for i in range(3): # type

                # Draw number of emails
                N_sim[i] = np.random.randint(self.N_lower[i], self.N_upper[i]+1, 1)
               
                # simulate whether each email is essential or not
                binary_essential = np.random.binomial(1, self.Pr[i], N_sim[i])
                binary_nonessential = 1 - binary_essential
                
                 # simulate times for steps (reading, action and writing times)
                rt = self.gammaDraw(self.Rt_guess[i], self.Rt_sd[i], N_sim[i])
                at = self.gammaDraw(self.At_guess[i], self.At_sd[i], N_sim[i])
                wt = self.gammaDraw(self.Wt_guess[i], self.Wt_sd[i], N_sim[i])

                # Derive total time by type
                    # summed across steps
                # add to matrix
                total_time_by_type[s,i] = rt.sum()+at.sum()+wt.sum()
                total_time_by_type_essential[s,i] = np.sum( (rt + at + wt) * binary_essential)
                total_time_by_type_nonessential[s,i] = np.sum( (rt + at + wt) * binary_nonessential)

                # add types to list of arrays
                rt_all_types[i] = rt
                at_all_types[i] = at
                wt_all_types[i] = wt
                # rt, at and wt are discarded each iteration of t

            rt_total[s] = sum(np.sum(array) for array in rt_all_types)
            at_total[s] = sum(np.sum(array) for array in at_all_types)
            wt_total[s] = sum(np.sum(array) for array in wt_all_types)

            # total number of emails
            N_total_vec[s] = N_sim.sum()

        # each element is of t_total_vec is the same as rowwise sum of total_time_by_type
        t_total_vec = np.sum(total_time_by_type, axis=1)
        t_essential_vec = np.sum(total_time_by_type_essential, axis=1)
        t_nonessential_vec = np.sum(total_time_by_type_nonessential, axis=1)

        # assign as attributes
        self.rt_total_vec = rt_total
        self.at_total_vec = at_total
        self.wt_total_vec = wt_total
        self.N_total_vec = N_total_vec
        self.total_time_by_type = total_time_by_type

        # get key output for pie charts
        self.median_total_type = np.median(total_time_by_type, axis=0)
        self.median_total_essential = np.median(t_essential_vec)
        self.median_total_nonessential = np.median(t_nonessential_vec)

        # format output
        self.rt_total_sum = self.num2Char(self.rt_total_vec)
        self.wt_total_sum = self.num2Char(self.at_total_vec)
        self.at_total_sum = self.num2Char(self.wt_total_vec)

        ## ----
        # OUTPUTS FOR DASHBOARD
        ## ----
        self.t_total_sum = self.num2Char(t_total_vec)
        self.t_essential_sum = self.num2Char(t_essential_vec)
        self.t_nonessential_sum = self.num2Char(t_nonessential_vec)
        self.N_total_sum = self.num2Char2(self.N_total_vec)

        # Staff values
        self.staff_total = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type, axis=1)/60) )
        self.staff_total_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type, axis=1)/60) )
        self.staff_essential = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type_essential, axis=1)/60) )
        self.staff_essential_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type_essential, axis=1)/60) )
        self.staff_nonessential = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type_nonessential, axis=1)/60) )
        self.staff_nonessential_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type_nonessential, axis=1)/60) )