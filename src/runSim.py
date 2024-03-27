import numpy as np
import matplotlib.pyplot as plt

def gammaDraw(mu, sigma, n):
    # redefine as standard parameters for gamma
    k = mu**2 / sigma**2
    theta = sigma**2 / mu
    # Simulate data from Gamma distribution
    return np.random.gamma(k, theta, n)

def num2Char(x):
    int95 = np.percentile(x, [2.5, 97.5])
    return "{:.2f} ({:.2f}, {:.2f})".format(np.median(x), 
                                            int95[0], int95[1]),

def ReadingTimeDistribution(N_lower, N_upper, point, lower, upper):
    """
    Simulates the distribution of total reading times based on varying numbers of emails
    received across three different types, each with its own reading time distribution. 
    This function generates 1000 simulations where, for each, the total reading time and 
    total number of emails received are calculated. The reading time for each email is drawn 
    from a gamma distribution, with the parameters determined by input mean values (`point`)
    and derived standard deviations from specified confidence intervals (`lower`, `upper`).

    Parameters:
    - N_lower (array-like of int): The lower bounds for the number of emails received  for each of the three types.
    - N_upper (array-like of int): The upper bounds for the number of emails received for each of the three types.
    - point (array-like of float): Mean (or 'point') reading time for each email type.
    - lower (array-like of float): Lower bounds of the 95% confidence interval for the mean reading times.
    - upper (array-like of float): Upper bounds of the 95% confidence interval for the mean reading times.

    Returns:
    - A dictionary containing:
        - 'read': The formatted string representation of the total reading times across all simulations.
        - 'number': The formatted string representation of the total number of emails received across all simulations.
        - 'figure': A matplotlib Figure object of the histogram plotting the distribution of total reading times.
        - 'axis': A matplotlib Axes object associated with the figure.

    Note:
    - The standard deviation used for gamma distribution draws is calculated from the provided
      confidence interval width, assuming the distribution does not imply symmetry around the mean.
    - It is required that the function `gammaDraw` exists and is capable of drawing samples
      from a gamma distribution given the mean, standard deviation, and sample size.
    - The function `num2Char` is assumed to convert numerical arrays to their string representations.

    Example:
    >>> N_lower = [10, 20, 15]
    >>> N_upper = [50, 100, 75]
    >>> point = [1.2, 2.5, 0.9]
    >>> lower = [1, 2, 0.8]
    >>> upper = [1.4, 3, 1]
    >>> result = ReadingTimeDistribution(N_lower, N_upper, point, lower, upper)
    >>> print(result['read'], result['number'])
    """
    # Convert interval to standard deviation
    sd_input = (upper - lower)/3.92 # doesn't assume symmetry

    # Loop 1000 times
    rt_total = np.zeros(1000)
    N_total = np.zeros(1000)
    for t in range(1000):

        # create vector of read times
        rt = np.empty(0)
        N_sim = np.zeros(3, dtype=int)
        for i in range(3):
            # simulate number of emails sent for each type
            N_sim[i] = np.random.randint( N_lower[i], N_upper[i], 1 )
            # simulate read times for each email
            rt = np.append( rt, gammaDraw(point[i],sd_input[i],N_sim[i]) )

        # derive totals and format for output
            rt_total[t] = rt.sum()
            N_total[t] = N_sim.sum()

    # create histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(rt_total, bins=30, density=True, alpha=0.6, color='g')

    # formatted_output 
    return {'read': num2Char(rt_total),
            'number': num2Char(N_total),
            'figure': fig,
            'axis': ax}

# Test the function
this = ReadingTimeDistribution(N_lower=np.array([5,15,3]),
                               N_upper=np.array([10,20,5]),
                               point=np.array([6,0.5,0.2]),
                               lower=np.array([2,0.1,0.1]),
                               upper=np.array([10,1,1]))

this['figure'].show()




