import numpy as np
import scipy.stats as stats
import plotly.express as px

class EmailReadingSimulation:
    def __init__(self, 
                TeamSize,
                Pay,
                Period,
                Pr):
        
        # Assign all parameters to instance variables of the same name
        for name, value in locals().items():
            if name != 'self':
                setattr(self, name, value)
        
    def setupDim(self, N, Rt, At, Wt):
        
        # Assign all parameters to instance variables of the same name
        for name, value in locals().items():
            if name != 'self':
                setattr(self, name, value)
        
    def setupSim(self, 
                 N_lower, N_upper, 
                 Rt_lower, Rt_upper,
                 At_lower, At_upper,
                 Wt_lower, Wt_upper):
        
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

    def num2Char(self, x, include_confidence_interval=True):
        """Convert numerical array to formatted string representation."""
        if include_confidence_interval:
            int95 = np.percentile(x, [2.5, 97.5])
            return "{:.1f} ({:.1f} - {:.1f})".format(np.median(x), int95[0], int95[1])
        else:
            return "{:.1f}".format(np.median(x)) 
    
    def num2Char2(self, x, include_confidence_interval=True):
        """Convert numerical array to formatted string representation."""
        if include_confidence_interval:
            int95 = np.percentile(x, [2.5, 97.5])
            return "{} ({} - {})".format(int(np.median(x)), int(int95[0]), int(int95[1]))
        else:
            return "{}".format(int(np.median(x)))
    
    def num2Char_dollars(self, x, include_confidence_interval=True):
        """Convert numerical array to formatted string representation."""
        if include_confidence_interval:
            int95 = np.percentile(x, [2.5, 97.5])
            return "${:,.0f} (${:,.0f} - ${:,.0f})".format(np.median(x), int95[0], int95[1])
        else:
            return "${:,.0f}".format(np.median(x))

    def simulate(self):
        """Simulate the distribution of total reading times."""
        n_sims = 500
        rt_total = np.zeros(n_sims)
        at_total = np.zeros(n_sims)
        wt_total = np.zeros(n_sims)
        t_total_vec = np.zeros(n_sims)
        t_essential_vec = np.zeros(n_sims)
        t_nonessential_vec = np.zeros(n_sims)
        N_total_vec = np.zeros(n_sims)
        total_time_by_type = np.zeros([n_sims,3])
        total_time_by_type_essential = np.zeros([n_sims,3])
        total_time_by_type_nonessential = np.zeros([n_sims,3])

        # run for n_sims iterations
        for s in range(n_sims):
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

        # format output
        self.rt_total_sum = self.num2Char(rt_total)
        self.at_total_sum = self.num2Char(at_total)
        self.wt_total_sum = self.num2Char(wt_total)

        ## ----
        # OUTPUTS FOR DASHBOARD
        ## ----

        # get key output for pie charts
        self.median_total_type = np.median(total_time_by_type, axis=0)
        self.median_total_essential = np.median(t_essential_vec)
        self.median_total_nonessential = np.median(t_nonessential_vec)

        self.t_total_sum = self.num2Char(t_total_vec/60)
        self.t_essential_sum = self.num2Char(t_essential_vec/60)
        self.t_nonessential_sum = self.num2Char(t_nonessential_vec/60)
        self.N_total_sum = self.num2Char2(N_total_vec)

        # Staff values
        self.staff_total = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type, axis=1)/60) )
        self.staff_total_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type, axis=1)/60) )
        self.staff_essential = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type_essential, axis=1)/60) )
        self.staff_essential_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type_essential, axis=1)/60) )
        self.staff_nonessential = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type_nonessential, axis=1)/60) )
        self.staff_nonessential_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type_nonessential, axis=1)/60) )

    def deterministic(self):

        # Create totals per type
        total_time_by_type = np.zeros(3)
        total_time_by_type_essential = np.zeros(3)
        total_time_by_type_nonessential = np.zeros(3)

        # create list of lists to store vectors of times for each type
        rt_all_types = [[], [], []]
        at_all_types = [[], [], []]
        wt_all_types = [[], [], []]

        # initilise number of emails of each type
        N_sim = np.zeros(3, dtype=int)

        for i in range(3): # type

            # Draw number of emails
            N_sim[i] = self.N[i]
            
                # simulate times for steps (reading, action and writing times)
            rt = np.full(N_sim[i], self.Rt[i])
            at = np.full(N_sim[i], self.At[i])
            wt = np.full(N_sim[i], self.Wt[i])

            # Derive total time by type
                # summed across steps
            # add to matrix
            total_time_by_type[i] = rt.sum()+at.sum()+wt.sum()
            total_time_by_type_essential[i] = np.sum( (rt + at + wt) ) * self.Pr[i]
            total_time_by_type_nonessential[i] = np.sum( (rt + at + wt) ) * (1 - self.Pr[i])

            # add types to list of arrays
            rt_all_types[i] = rt
            at_all_types[i] = at
            wt_all_types[i] = wt
            # rt, at and wt are discarded each iteration of t

        rt_total = sum(np.sum(array) for array in rt_all_types)
        at_total = sum(np.sum(array) for array in at_all_types)
        wt_total = sum(np.sum(array) for array in wt_all_types)

        # total number of emails
        N_total_vec = N_sim.sum()

        # each element is of t_total_vec is the same as row-wise sum of total_time_by_type
        t_total_vec = np.sum(total_time_by_type)
        t_essential_vec = np.sum(total_time_by_type_essential)
        t_nonessential_vec = np.sum(total_time_by_type_nonessential)

        # get key output for pie charts
        self.median_total_type = total_time_by_type
        self.median_total_essential = t_essential_vec
        self.median_total_nonessential = t_nonessential_vec

        # format output
        self.rt_total_sum = self.num2Char(rt_total, include_confidence_interval=False)
        self.at_total_sum = self.num2Char(at_total, include_confidence_interval=False)
        self.wt_total_sum = self.num2Char(wt_total, include_confidence_interval=False)

        ## ----
        # OUTPUTS FOR DASHBOARD
        ## ----
        self.t_total_sum = self.num2Char(t_total_vec/60, include_confidence_interval=False)
        self.t_essential_sum = self.num2Char(t_essential_vec/60, include_confidence_interval=False)
        self.t_nonessential_sum = self.num2Char(t_nonessential_vec/60, include_confidence_interval=False)
        self.N_total_sum = self.num2Char2(N_total_vec, include_confidence_interval=False)

        # Staff values
        self.staff_total = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type)/60), include_confidence_interval=False )
        self.staff_total_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type)/60), include_confidence_interval=False )
        self.staff_essential = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type_essential)/60), include_confidence_interval=False )
        self.staff_essential_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type_essential)/60), include_confidence_interval=False )
        self.staff_nonessential = self.num2Char2( (260/self.Period) * (np.sum(self.TeamSize * total_time_by_type_nonessential)/60), include_confidence_interval=False )
        self.staff_nonessential_cost = self.num2Char_dollars( (260/self.Period) * self.Pay * (np.sum(self.TeamSize * total_time_by_type_nonessential)/60), include_confidence_interval=False )

def plot_gamma_distribution(lower, upper):
    """
    Plot a gamma distribution based on a specified range.
    
    This function calculates the mean and standard deviation of a gamma distribution
    given the lower and upper bounds of a range. It then calculates the shape (alpha)
    and scale (theta) parameters of the gamma distribution from the mean and standard
    deviation. The function plots the probability density function (PDF) of the
    gamma distribution over a range of values.
    
    Parameters:
    - lower (float): The lower bound of the range from which the mean and standard 
      deviation are calculated.
    - upper (float): The upper bound of the range from which the mean and standard 
      deviation are calculated.
    
    The mean is calculated as the midpoint of the lower and upper bounds, and the 
    standard deviation is derived based on the assumption that the range represents 
    approximately 99.7% (3 sigma) of the data values.
    
    Returns:
    None. This function directly plots the gamma distribution using matplotlib.
    
    Example:
    >>> plot_gamma_distribution(5, 15)
    This will plot a gamma distribution with a mean of 10 and a standard deviation
    calculated based on the input range.
    """
    # Get mean and std from low and upper 
    mean = (upper + lower) / 2
    std = (upper - lower) / 3.92

    # Calculate alpha and theta from mean and std
    alpha = mean**2 / std**2
    theta = std**2 / mean
    
    # Define the gamma distribution
    gamma_dist = stats.gamma(a=alpha, scale=theta)
    
    # Generate x values
    x = np.linspace(0, mean + 4*std, 100)
    
    # Calculate the PDF values for x
    pdf = gamma_dist.pdf(x)
    
    # Plotting
    fig = px.line(x=x, y=pdf)
    fig.update_layout(title='',
                      yaxis_title='Probability',
                      xaxis_title='Time (mins)')


    return fig



