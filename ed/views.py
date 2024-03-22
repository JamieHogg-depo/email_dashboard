from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.offline

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

def teams_stochastic(request):

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

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/teams_stochastic.html', context) # pass dictionary