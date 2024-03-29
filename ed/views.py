from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.offline
import matplotlib.pyplot as plt
import ed.EmailReadingSimulation as ed

## ----------------------------------------------------------------------------
## FUNCTIONS ## -------------------------------------------------------------------
## ----------------------------------------------------------------------------
class EmailProductivityCalculator:
    def __init__(self, params): # params as dict
        self.N = params.get('N', 1)  # Team size
        self.Ep = params.get('Ep', 1)  # Emails sent per person per period
        self.Tr = params.get('Tr', 5)  # Time to read an email in seconds
        self.Ra = params.get('Ra', 1)  # Average recipients per email
        self.Pr = params.get('Pr', 0.5)  # Proportion of relevant emails
        self.PeriodSize_days = params.get('PeriodSize_days', 1)

        # probability of a single email from one employee going to another employee
            # Ra/(N-1) -> this equals 1 if Ra = N-1

        # average recipients per email must be less than or equal to N - 1

        self.emails_received = np.round(self.Ep * self.Ra, 2)
        self.emails_received_year = (260/self.PeriodSize_days) * self.emails_received

        # time spent reading - period
        self.period = {
            'total': np.round((self.emails_received * self.Tr) / 60, 2),
            'notrelevant': np.round((self.emails_received * self.Tr * (1 - self.Pr)) / 60, 2)
        }

        # time spent reading - year
            # 52 * 5 = 260 work days in a year
        self.year = {
            # present yearly figures in hours
            'total': np.round( ((260/self.PeriodSize_days) * self.period['total']) / 60, 2),
            'notrelevant': np.round( ((260/self.PeriodSize_days) * self.period['notrelevant']) / 60, 2) 
        }

def landing(request):
    return render(request, 'ed/landing.html')

## ----------------------------------------------------------------------------
## BASIC ## -------------------------------------------------------------------
## ----------------------------------------------------------------------------
def basic(request):

    context = { # this is a dictionary with default value 
        'N': 1,  
        'Ep': 1,  
        'Tr': 5,
        'Ra': 1,
        'Pr': 0.5,
        'PeriodSize_days': 1,
    }

    if request.method == 'POST':
        # Retrieve numbers from the form
        context['N'] = int(request.POST.get('N', 0))
        context['PeriodSize_days'] = int(request.POST.get('PeriodSize_days', 0))
        context['Ep'] = int(request.POST.get('Ep', 0))
        context['Tr'] = int(request.POST.get('Tr', 0))
        context['Ra'] = int(request.POST.get('Ra', 0))
        context['Pr'] = float(request.POST.get('Pr', 0.0))
        
        # Use class to provide outputs
        calculator = EmailProductivityCalculator(context)
        context['emails_received'] = calculator.emails_received
        context['emails_received_year'] = calculator.emails_received_year

        # Time per person
        context['time_per_person'] = calculator.period['total']
        context['time_per_person_notrelevant'] = calculator.period['notrelevant']
        context['time_per_year'] = calculator.year['total']
        context['time_per_year_notrelevant'] = calculator.year['notrelevant']

        # staff hours
        context['time_staff'] = np.round( (calculator.period['total']*calculator.N)/60 , 2)
        context['time_staff_notrelevant'] = np.round( (calculator.period['notrelevant']*calculator.N)/60 , 2)

        # Create pie chart
        fig = px.pie(values=[calculator.period['total'] - calculator.period['notrelevant'], 
                             calculator.period['notrelevant']], 
                             names=['Essential', 'Non-Essential'],
                             color_discrete_sequence=['#ff9999', '#99ff99'])
        fig.update_layout(
            title="Total time reading emails",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        context['graph'] = plotly.offline.plot(fig, output_type='div')

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/basic.html', context) # pass dictionary

## ----------------------------------------------------------------------------
## TEAMS ## -------------------------------------------------------------------
## ----------------------------------------------------------------------------
def teams(request):

    context = { # this is a dictionary with default value 
        'N_1': 10, 
        'N_2': 10, 
        'PeriodSize_days': 1,
        'Tr': 10,
        'Ep_1': 1,  'Ep_2': 1, 
        'Ra_1': 1, 'Ra_2': 1,
        'Pr_1': 0.5, 'Pr_2': 0.5
    }

    if request.method == 'POST':
        # Retrieve numbers from the form
        context['Tr'] = int(request.POST.get('Tr', 0))
        context['PeriodSize_days'] = int(request.POST.get('PeriodSize_days', 0))
        context['N_1'] = int(request.POST.get('N_1', 0))
        context['N_2'] = int(request.POST.get('N_2', 0))
        context['Ep_1'] = int(request.POST.get('Ep_1', 0))
        context['Ra_1'] = int(request.POST.get('Ra_1', 0))
        context['Pr_1'] = float(request.POST.get('Pr_1', 0.0))
        context['Ep_2'] = int(request.POST.get('Ep_2', 0))
        context['Ra_2'] = int(request.POST.get('Ra_2', 0))
        context['Pr_2'] = float(request.POST.get('Pr_2', 0.0))

        # Team 1
        params1 = {'Tr': int(request.POST.get('Tr', 0)),
                   'PeriodSize_days': context['PeriodSize_days'],
                   'N_1': context['N_1'],
                   'Ep': int(request.POST.get('Ep_1', 0)),  
                   'Ra': int(request.POST.get('Ra_1', 0)),
                   'Pr': float(request.POST.get('Pr_1', 0.0))}
        cal1 = EmailProductivityCalculator(params1)

        # Team 2
        params2 = {'Tr': int(request.POST.get('Tr', 0)),
                   'PeriodSize_days': context['PeriodSize_days'],
                   'Ep': int(request.POST.get('Ep_2', 0)),  
                   'N': context['N_2'],
                   'Ra': int(request.POST.get('Ra_2', 0)),
                   'Pr': float(request.POST.get('Pr_2', 0.0))}
        cal2 = EmailProductivityCalculator(params2)
        
        # Use class to provide outputs
        context['emails_received'] = cal1.emails_received + cal2.emails_received
        context['emails_received_year'] = cal1.emails_received_year + cal2.emails_received_year

        # Time per person
        context['time_per_person'] = cal1.period['total']
        context['time_per_person_notrelevant'] = cal1.period['notrelevant']
        context['time_per_year'] = cal1.year['total']
        context['time_per_year_notrelevant'] = cal1.year['notrelevant']

        # staff hours
        context['time_staff'] = np.round( (cal1.period['total']*cal1.N + cal2.period['total']*cal2.N)/60 , 2)
        context['time_staff_notrelevant'] = np.round( (cal1.period['notrelevant']*cal1.N + cal2.period['notrelevant']*cal2.N)/60 , 2)

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/teams.html', context) # pass dictionary

## ----------------------------------------------------------------------------
## TEAMS ## -------------------------------------------------------------------
## ----------------------------------------------------------------------------
def teams_stochastic(request):

    # create context dictionary
    context = {}
    context['TeamSize'] = 20
    context['Pay'] = 80
    context['Period'] = 1
    for type_num in range(1,4):
        context[f'N_lower{type_num}'] = 1
        context[f'N_upper{type_num}'] = 1
        context[f'Rt_lower{type_num}'] = 0.9
        context[f'Rt_upper{type_num}'] = 1.1
        context[f'Wt_lower{type_num}'] = 0.9
        context[f'Wt_upper{type_num}'] = 1.1
        context[f'At_lower{type_num}'] = 0.9
        context[f'At_upper{type_num}'] = 1.1
        context[f'Pr_rel{type_num}'] = 1

    # create empty lists
    N_lower = []
    N_upper = []
    Rt_lower = []
    Rt_upper = []
    At_lower = []
    At_upper = []
    Wt_lower = []
    Wt_upper = []
    Pr = []

    if request.method == 'POST':
        # Retrieve numbers from the form
        context['TeamSize'] = int(request.POST.get('TeamSize', 0))
        context['Pay'] = int(request.POST.get('Pay', 0))
        context['Period'] = int(request.POST.get('Period', 0))
        for type_num in range(1,4):  # This will loop through 1, 2, 3
            # for Context vector
            context[f'N_lower{type_num}'] = int(request.POST.get(f'N_lower{type_num}', 0))
            context[f'N_upper{type_num}'] = int(request.POST.get(f'N_upper{type_num}', 0))
            context[f'Rt_lower{type_num}'] = float(request.POST.get(f'Rt_lower{type_num}', 0.0))
            context[f'Rt_upper{type_num}'] = float(request.POST.get(f'Rt_upper{type_num}', 0.0))
            context[f'At_lower{type_num}'] = float(request.POST.get(f'At_lower{type_num}', 0.0))
            context[f'At_upper{type_num}'] = float(request.POST.get(f'At_upper{type_num}', 0.0))
            context[f'Wt_lower{type_num}'] = float(request.POST.get(f'Wt_lower{type_num}', 0.0))
            context[f'Wt_upper{type_num}'] = float(request.POST.get(f'Wt_upper{type_num}', 0.0))
            context[f'Pr_rel{type_num}'] = float(request.POST.get(f'Pr_rel{type_num}', 0.0))
            # for Function
            N_lower.append(int(request.POST.get(f'N_lower{type_num}', 0)))
            N_upper.append(int(request.POST.get(f'N_upper{type_num}', 0)))
            Rt_lower.append(float(request.POST.get(f'Rt_lower{type_num}', 0.0)))
            Rt_upper.append(float(request.POST.get(f'Rt_upper{type_num}', 0.0)))
            At_lower.append(float(request.POST.get(f'At_lower{type_num}', 0.0)))
            At_upper.append(float(request.POST.get(f'At_upper{type_num}', 0.0)))
            Wt_lower.append(float(request.POST.get(f'Wt_lower{type_num}', 0.0)))
            Wt_upper.append(float(request.POST.get(f'Wt_upper{type_num}', 0.0)))
            Pr.append(float(request.POST.get(f'Pr_rel{type_num}', 0.0)))

            if context[f'N_lower{type_num}'] > context[f'N_upper{type_num}']:
                error_message = "Error: Upper value must be greater than lower value.<br>Please click back in your browser and check your values for Emails received."
                return HttpResponseBadRequest(error_message)
            
            if context[f'Rt_lower{type_num}'] >= context[f'Rt_upper{type_num}']:
                error_message = "Error: Upper value must be greater than lower value.<br>Please click back in your browser and check your values for Read time."
                return HttpResponseBadRequest(error_message)
            
            if context[f'At_lower{type_num}'] >= context[f'At_upper{type_num}']:
                error_message = "Error: Upper value must be greater than lower value.<br>Please click back in your browser and check your values for Action time."
                return HttpResponseBadRequest(error_message)
            
            if context[f'Wt_lower{type_num}'] >= context[f'Wt_upper{type_num}']:
                error_message = "Error: Upper value must be greater than lower value.<br>Please click back in your browser and check your values for Response time."
                return HttpResponseBadRequest(error_message)

        # Run simulation
        sm = ed.EmailReadingSimulation(
            TeamSize=context['TeamSize'],
            Pay=context['Pay'],
            Period=context['Period'],
            N_lower=np.array(N_lower),
            N_upper=np.array(N_upper),
            Rt_lower=np.array(Rt_lower),
            Rt_upper=np.array(At_upper),
            At_lower=np.array(At_lower),
            At_upper=np.array(Rt_upper),
            Wt_lower=np.array(Wt_lower),
            Wt_upper=np.array(Wt_upper),
            Pr = np.array(Pr)
        )

        # update attributes with simulation
        sm.simulate()
        
        # Use class to provide outputs
        context['N_total_out'] = sm.N_total_sum
        context['t_total_sum'] = sm.t_total_sum
        context['t_essential_sum'] = sm.t_essential_sum
        context['t_nonessential_sum'] = sm.t_nonessential_sum

        # staff values
        context['staff_total'] = sm.staff_total
        context['staff_total_cost'] = sm.staff_total_cost
        context['staff_essential'] = sm.staff_essential
        context['staff_essential_cost'] = sm.staff_essential_cost
        context['staff_nonessential'] = sm.staff_nonessential
        context['staff_nonessential_cost'] = sm.staff_nonessential_cost

        # Create pie chart by type
        fig = px.pie(values=sm.median_total_type, 
                     names=['Type 1', 'Type 2', 'Type 3'],
                     color_discrete_sequence=['#6e8ab7', '#E59538', '#5B7553'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            width=450,  # Specify the width
            height=450,  # Specify the height
            font=dict(size=20)
        )
        context['pie_type'] = plotly.offline.plot(fig, output_type='div')

        # Create pie chart by relevance
        fig = px.pie(values=[sm.median_total_essential, sm.median_total_nonessential], 
                     names=['Essential', 'Nonessential'],
                     color_discrete_sequence=['#cccccc', '#f76565'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            width=450,  # Specify the width
            height=450,  # Specify the height
            font=dict(size=20)
        )
        context['pie_essential'] = plotly.offline.plot(fig, output_type='div')

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/teams_stochastic.html', context) # pass dictionary