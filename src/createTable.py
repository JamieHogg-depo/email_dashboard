import numpy as np
import pandas as pd
import plotly.express as px
import plotly.offline
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import ed.EmailReadingSimulation as ed

# function to turn character vecotr of prop email types into np array
def convert(N, Prop_email_type):
    numeric_parts = [float(part) for part in Prop_email_type.split(',')]
    return np.round(N*(np.array(numeric_parts)/100),0)

# Create grid of input parameters
TeamSize_l = [10,20,50]
N_l = [50, 120]
prop_emails_type_l = ['100,0,0', '0,100,0', '0,0,100', '33,33,34', '50,50,0']
index=pd.MultiIndex.from_product([TeamSize_l, N_l , prop_emails_type_l], names=['Number of staff', "Total Number of Emails", "Prop_emails_type"])
grid = pd.DataFrame(index=index).reset_index()
grid['TotalHoursEssential'] = None
grid['TotalHoursNonessential'] = None
grid['AnnualCostAllStaffNonessential'] = None

for i, row in grid.iterrows():

    # Create class instance 
    sm = ed.EmailReadingSimulation(
        TeamSize=row['Number of staff'],
        Pay=80,
        Period=1,
        Pr = np.array([1,0.5,0.1])
    ) 

    # setup deterministic attributes
    sm.setupDim(N=convert(row['Total Number of Emails'], row['Prop_emails_type']),
                Rt=np.array([2,1,1]),
                At=np.array([3,1,1]),
                Wt=np.array([1,0.5,0]))

    # update attributes with simulation
    sm.deterministic()

    # Use class to provide outputs
    grid.loc[i,'TotalHoursEssential'] = sm.t_essential_sum
    grid.loc[i,'TotalHoursNonessential'] = sm.t_nonessential_sum
    grid.loc[i,'AnnualCostAllStaffNonessential'] = sm.staff_nonessential_cost

grid.to_csv('src/ReportTable.csv', index=False)

