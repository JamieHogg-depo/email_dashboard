import ed.EmailReadingSimulation as ed
import numpy as np
from memory_profiler import memory_usage

# Create class instance 
sm = ed.EmailReadingSimulation(TeamSize=np.array([20]),
                               Pay=np.array([80]),
                               Period=np.array([1]),
                               Pr = np.array([100,50,10])/100
) 

# setup simulation attributes
sm.setupSim(N_lower=np.array([20,30,40]),
            N_upper=np.array([25,35,45]),
            Rt_lower=np.array([1,1,1]),
            Rt_upper=np.array([2,2,2]),
            At_lower=np.array([1,1,1]),
            At_upper=np.array([2,2,2]),
            Wt_lower=np.array([1,1,1]),
            Wt_upper=np.array([2,2,2]))

# update attributes with simulation
sm.simulate()

mem_us = memory_usage(sm.simulate)
print('Memory usage (in chunks of .1 seconds): %s' % mem_us)
print('Maximum memory usage: %s' % max(mem_us))

def load_packages():
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import matplotlib.pyplot as plt
    import ed.EmailReadingSimulation as ed

memory_after_imports = memory_usage((load_packages, ))
print(f"Memory Usage After Imports: {memory_after_imports} MB")