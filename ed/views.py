from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np

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

def home(request):

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
    return render(request, 'ed/home.html', context) # pass dictionary

def teams(request):

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