import numpy as np
import matplotlib.pyplot as plt

N_lower = np.array([1,1,1])
N_upper = np.array([2,2,2])
Rt_lower = np.array([1,1,1])
Rt_upper = np.array([2,2,2])
At_lower = np.array([1,1,1])
At_upper = np.array([2,2,2])
Wt_lower = np.array([1,1,1])
Wt_upper = np.array([2,2,2])
Pr = np.array([1.0,1.0,1.0])
       
# derived values
Rt_guess = (Rt_upper - Rt_lower) / 2
Rt_sd = (Rt_upper - Rt_lower) / 3.92  # Standard deviation calculation
At_guess = (At_upper - At_lower) / 2
At_sd = (At_upper - At_lower) / 3.92  # Standard deviation calculation
Wt_guess = (Wt_upper - Wt_lower) / 2
Wt_sd = (Wt_upper - Wt_lower) / 3.92  # Standard deviation calculation

# initialise
rt_total_vec = None
at_total_vec = None
wt_total_vec = None
N_total_vec = None
rt_total_sum = None
at_total_sum = None
wt_total_sum = None
N_total_sum = None

def gammaDraw(mu, sigma, n):
    """Draw samples from a gamma distribution."""
    k = mu ** 2 / sigma ** 2
    theta = sigma ** 2 / mu
    return np.random.gamma(k, theta, n)

def num2Char(x):
    """Convert numerical array to formatted string representation."""
    int95 = np.percentile(x, [2.5, 97.5])
    return "{:.2f} ({:.2f}, {:.2f})".format(np.median(x), int95[0], int95[1])

def num2Char2(x):
    """Convert numerical array to formatted string representation."""
    int95 = np.percentile(x, [2.5, 97.5])
    return "{} ({}, {})".format(int(np.median(x)), int(int95[0]), int(int95[1]))

# run simulate function
rt_total = np.zeros(1000)
at_total = np.zeros(1000)
wt_total = np.zeros(1000)
t_total = np.zeros(1000)
N_total = np.zeros(1000)
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
        N_sim[i] = np.random.randint(N_lower[i], N_upper[i]+1, 1)
        
        # simulate whether each email is essential or not
        binary_essential = np.random.binomial(1, Pr[i], N_sim[i])
        binary_nonessential = 1 - binary_essential
        
            # simulate reading, action and writing times
        rt = gammaDraw(Rt_guess[i], Rt_sd[i], N_sim[i])
        at = gammaDraw(At_guess[i], At_sd[i], N_sim[i])
        wt = gammaDraw(Wt_guess[i], Wt_sd[i], N_sim[i])

        # Derive total time by type
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
    t_total[s] = rt_total[s] + at_total[s] + wt_total[s]
    N_total[s] = N_sim.sum()

# assign as attributes
rt_total_vec = rt_total
at_total_vec = at_total
wt_total_vec = wt_total
t_total_vec = t_total
N_total_vec = N_total
total_time_by_type = total_time_by_type
median_total_type = np.median(total_time_by_type, axis=0)
median_total_type_essential = np.median(total_time_by_type_essential, axis=0)
median_total_type_nonessential = np.median(total_time_by_type_nonessential, axis=0)

# format output
rt_total_sum = num2Char(rt_total_vec)
wt_total_sum = num2Char(at_total_vec)
at_total_sum = num2Char(wt_total_vec)
t_total_sum = num2Char(t_total_vec)
N_total_sum = num2Char2(N_total_vec)