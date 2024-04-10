from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.offline
import plotly.graph_objects as go
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
## ADVANCED ## ----------------------------------------------------------------
## ----------------------------------------------------------------------------
def advanced(request):

    # create context dictionary
    context = {}
    context['TeamSize'] = 20
    context['Pay'] = 80
    context['Period'] = 1
    # default names
    context['Name1'], context['Name2'], context['Name3']  = "All relevant", "50-50", "Low relevance"
    # default relevance
    context['Pr_rel1'], context['Pr_rel2'], context['Pr_rel3'] = 100, 50, 10
    for type_num in range(1,4):
        context[f'N_lower{type_num}'] = 1
        context[f'N_upper{type_num}'] = 1
        context[f'Rt_lower{type_num}'] = 0.9
        context[f'Rt_upper{type_num}'] = 1.1
        context[f'Wt_lower{type_num}'] = 0.9
        context[f'Wt_upper{type_num}'] = 1.1
        context[f'At_lower{type_num}'] = 0.9
        context[f'At_upper{type_num}'] = 1.1

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
        # Retrieve names from form
        context['Name1'] = request.POST.get('Name1')
        context['Name2'] = request.POST.get('Name2')
        context['Name3'] = request.POST.get('Name3')
        # Retrieve numbers from the form
        context['TeamSize'] = int(request.POST.get('TeamSize', 0))
        context['Pay'] = int(request.POST.get('Pay', 0))
        context['Period'] = int(request.POST.get('Period', 0))
        for type_num in range(1,4):  # This will loop through 1, 2, 3

            ## ----
            ## ERRORS/WARNING MESSAGES ## 
            ## ----

            keys = ['N_lower', 'N_upper', 'Rt_lower', 'Rt_upper', 'At_lower', 'At_upper', 'Wt_lower', 'Wt_upper', 'Pr_rel']

            # Ensure all values are greater or equal to 0
                    # Iterate through keys to retrieve and validate values
            for key in keys:
                # Retrieve the value as a float or int based on the key
                value = float(request.POST.get(f'{key}{type_num}', 0.0)) if 'Pr_rel' not in key else int(request.POST.get(f'{key}{type_num}', 0))
                
                # Check if any value is less than zero
                if value < 0:
                    # If a value is less than zero, return a bad request response with an error message
                    error_message = "Error: All inputs must be greater than or equal to zero.<br>Please click back in your browser and check your inputs."
                    return HttpResponseBadRequest(error_message)
                
                # Add the validated value to the context
                context[f'{key}{type_num}'] = value

            # Ensure pr is between 0 and 100
            if not (0 <= int(request.POST.get(f'Pr_rel{type_num}', 0)) <= 100):
                error_message = "Error: 'Percentage of relevant' values must be between 0 and 100.<br>Please click back in your browser and check your inputs."
                return HttpResponseBadRequest(error_message)

            # specific errors
            if int(request.POST.get(f'N_lower{type_num}', 0)) > int(request.POST.get(f'N_upper{type_num}', 0)):
                error_message = "Error: Max value must be greater than Min value.<br>Please click back in your browser and check your values for 'Number of emails received'."
                return HttpResponseBadRequest(error_message)
            
            if float(request.POST.get(f'Rt_lower{type_num}', 0.0)) >= float(request.POST.get(f'Rt_upper{type_num}', 0.0)):
                error_message = "Error: Max value must be greater than Min value.<br>Please click back in your browser and check your values for 'Read'."
                return HttpResponseBadRequest(error_message)
            
            if float(request.POST.get(f'At_lower{type_num}', 0.0)) >= float(request.POST.get(f'At_upper{type_num}', 0.0)):
                error_message = "Error: Max value must be greater than Min value.<br>Please click back in your browser and check your values for 'Action'."
                return HttpResponseBadRequest(error_message)
            
            if float(request.POST.get(f'Wt_lower{type_num}', 0.0)) >= float(request.POST.get(f'Wt_upper{type_num}', 0.0)):
                error_message = "Error: Max value must be greater than Min value.<br>Please click back in your browser and check your values for 'Respond'."
                return HttpResponseBadRequest(error_message)

            ## ----
            ## ADD REQUESTS TO CONTEXT ## 
            ## ----

            # for Context vector
            context[f'N_lower{type_num}'] = int(request.POST.get(f'N_lower{type_num}', 0))
            context[f'N_upper{type_num}'] = int(request.POST.get(f'N_upper{type_num}', 0))
            context[f'Rt_lower{type_num}'] = float(request.POST.get(f'Rt_lower{type_num}', 0.0))
            context[f'Rt_upper{type_num}'] = float(request.POST.get(f'Rt_upper{type_num}', 0.0))
            context[f'At_lower{type_num}'] = float(request.POST.get(f'At_lower{type_num}', 0.0))
            context[f'At_upper{type_num}'] = float(request.POST.get(f'At_upper{type_num}', 0.0))
            context[f'Wt_lower{type_num}'] = float(request.POST.get(f'Wt_lower{type_num}', 0.0))
            context[f'Wt_upper{type_num}'] = float(request.POST.get(f'Wt_upper{type_num}', 0.0))
            context[f'Pr_rel{type_num}'] = int(request.POST.get(f'Pr_rel{type_num}', 0))
            # for Function
            N_lower.append(int(request.POST.get(f'N_lower{type_num}', 0)))
            N_upper.append(int(request.POST.get(f'N_upper{type_num}', 0)))
            Rt_lower.append(float(request.POST.get(f'Rt_lower{type_num}', 0.0)))
            Rt_upper.append(float(request.POST.get(f'Rt_upper{type_num}', 0.0)))
            At_lower.append(float(request.POST.get(f'At_lower{type_num}', 0.0)))
            At_upper.append(float(request.POST.get(f'At_upper{type_num}', 0.0)))
            Wt_lower.append(float(request.POST.get(f'Wt_lower{type_num}', 0.0)))
            Wt_upper.append(float(request.POST.get(f'Wt_upper{type_num}', 0.0)))
            Pr.append(int(request.POST.get(f'Pr_rel{type_num}', 0)))

        # Create class instance 
        sm = ed.EmailReadingSimulation(
            TeamSize=context['TeamSize'],
            Pay=context['Pay'],
            Period=context['Period'],
            Pr = np.array(Pr)/100
        ) 

        # setup simulation attributes
        sm.setupSim(N_lower=np.array(N_lower),
            N_upper=np.array(N_upper),
            Rt_lower=np.array(Rt_lower),
            Rt_upper=np.array(At_upper),
            At_lower=np.array(At_lower),
            At_upper=np.array(Rt_upper),
            Wt_lower=np.array(Wt_lower),
            Wt_upper=np.array(Wt_upper))

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
        pie_type_df = pd.DataFrame(data = {'values': sm.median_total_type,
                                           'labels': [context['Name1'], context['Name2'], context['Name3']]})
                                        #'labels': ['Type 1', 'Type 2', 'Type 3']})
        hover_text_template = f"<b>%{{label}}</b>: %{{value:.1f}} mins out of {sm.median_total_type.sum():.1f} mins"

        # create figure
        fig = go.Figure(data=[go.Pie(labels=pie_type_df['labels'], 
                                     values=pie_type_df['values'], 
                                     hovertemplate=hover_text_template,
                                     marker=dict(colors=['#6e8ab7', '#E59538', '#5B7553']))])
        fig.update_layout(
            title="Email type",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            width=450,  # Specify the width
            height=560,  # Specify the height
            font=dict(size=15),
            legend=dict(orientation="h",  # Set legend orientation to horizontal
                        yanchor="bottom"  # Anchor legend to the bottom
                        )
        )
        context['pie_type'] = plotly.offline.plot(fig, output_type='div')

    # Create pie chart by relevance
        pie_essential_df = pd.DataFrame(data = {'values': [sm.median_total_essential, sm.median_total_nonessential],
                                                'labels': ['Relevant', 'Irrelevant']})
        hover_text_template = f"<b>%{{label}}</b>: %{{value:.1f}} mins out of {(sm.median_total_essential + sm.median_total_nonessential):.1f} mins"

        # create figure
        fig = go.Figure(data=[go.Pie(labels=pie_essential_df['labels'], 
                                     values=pie_essential_df['values'], 
                                     hovertemplate=hover_text_template,
                                     marker=dict(colors=['#cccccc', '#f76565']))])
        fig.update_layout(
            title="Relevance",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            width=450,  # Specify the width
            height=560,  # Specify the height
            font=dict(size=15),
            legend=dict(orientation="h",  # Set legend orientation to horizontal
                        yanchor="bottom"  # Anchor legend to the bottom
                        )
        )
        context['pie_essential'] = plotly.offline.plot(fig, output_type='div')

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/advanced.html', context) # pass dictionary

## ----------------------------------------------------------------------------
## STANDARD ## ----------------------------------------------------------------
## ----------------------------------------------------------------------------
def standard(request):

    # create context dictionary
    context = {}
    context['TeamSize'] = 20
    context['Pay'] = 80
    context['Period'] = 1
    # default names
    context['Name1'], context['Name2'], context['Name3']  = "All relevant", "50-50", "Low relevance"
    # default relevance
    context['Pr_rel1'], context['Pr_rel2'], context['Pr_rel3'] = 100, 50, 10
    # loop
    for type_num in range(1,4):
        context[f'N_{type_num}'] = 1
        context[f'Rt_{type_num}'] = 1
        context[f'Wt_{type_num}'] = 1
        context[f'At_{type_num}'] = 1

    # create empty lists
    N = []
    Rt = []
    At = []
    Wt = []
    Pr = []

    if request.method == 'POST':
        # Retrieve names from form
        context['Name1'] = request.POST.get('Name1')
        context['Name2'] = request.POST.get('Name2')
        context['Name3'] = request.POST.get('Name3')
        # Retrieve numbers from the form
        context['TeamSize'] = int(request.POST.get('TeamSize', 0))
        context['Pay'] = int(request.POST.get('Pay', 0))
        context['Period'] = int(request.POST.get('Period', 0))
        for type_num in range(1,4):  # This will loop through 1, 2, 3

            ## ----
            ## ERRORS/WARNING MESSAGES ## 
            ## ----
            # Ensure all values are greater or equal to 0
                    # Iterate through keys to retrieve and validate values
            keys = ['N_', 'Rt_', 'At_', 'Wt_', 'Pr_rel']
            for key in keys:
                # Retrieve the value as a float or int based on the key
                value = float(request.POST.get(f'{key}{type_num}', 0.0)) if 'Pr_rel' not in key else int(request.POST.get(f'{key}{type_num}', 0))
                
                # Check if any value is less than zero
                if value < 0:
                    # If a value is less than zero, return a bad request response with an error message
                    error_message = "Error: All inputs must be greater than or equal to zero.<br>Please click back in your browser and check your inputs."
                    return HttpResponseBadRequest(error_message)
                
                # Add the validated value to the context
                context[f'{key}{type_num}'] = value

            # Ensure pr is between 0 and 100
            if not (0 <= int(request.POST.get(f'Pr_rel{type_num}', 0)) <= 100):
                error_message = "Error: 'Percentage of relevant' values must be between 0 and 100.<br>Please click back in your browser and check your inputs."
                return HttpResponseBadRequest(error_message)

            ## ----
            ## ADD REQUESTS TO CONTEXT ## 
            ## ----

            # for Context vector
            context[f'N_{type_num}'] = int(request.POST.get(f'N_{type_num}', 0))
            context[f'Rt_{type_num}'] = float(request.POST.get(f'Rt_{type_num}', 0.0))
            context[f'At_{type_num}'] = float(request.POST.get(f'At_{type_num}', 0.0))
            context[f'Wt_{type_num}'] = float(request.POST.get(f'Wt_{type_num}', 0.0))
            context[f'Pr_rel{type_num}'] = int(request.POST.get(f'Pr_rel{type_num}', 0))
            # for Function
            N.append(int(request.POST.get(f'N_{type_num}', 0)))
            Rt.append(float(request.POST.get(f'Rt_{type_num}', 0.0)))
            At.append(float(request.POST.get(f'At_{type_num}', 0.0)))
            Wt.append(float(request.POST.get(f'Wt_{type_num}', 0.0)))
            Pr.append(int(request.POST.get(f'Pr_rel{type_num}', 0)))

        # Create class instance 
        sm = ed.EmailReadingSimulation(
            TeamSize=context['TeamSize'],
            Pay=context['Pay'],
            Period=context['Period'],
            Pr = np.array(Pr)/100
        ) 

        # setup deterministic attributes
        sm.setupDim(N=np.array(N),
                    Rt=np.array(Rt),
                    At=np.array(At),
                    Wt=np.array(Wt))

        # update attributes with simulation
        sm.deterministic()
        
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
        pie_type_df = pd.DataFrame(data = {'values': sm.median_total_type,
                                           'labels': [context['Name1'], context['Name2'], context['Name3']]})
                                           #'labels': ['Type 1', 'Type 2', 'Type 3']})
        hover_text_template = f"<b>%{{label}}</b>: %{{value:.1f}} mins out of {sm.median_total_type.sum():.1f} mins"

        # create figure
        fig = go.Figure(data=[go.Pie(labels=pie_type_df['labels'], 
                                     values=pie_type_df['values'], 
                                     hovertemplate=hover_text_template,
                                     marker=dict(colors=['#6e8ab7', '#E59538', '#5B7553']))])
        fig.update_layout(
            title="Email type",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            #showlegend=False,
            width=450,  # Specify the width
            height=560,  # Specify the height
            font=dict(size=15),
            legend=dict(orientation="h",  # Set legend orientation to horizontal
                        yanchor="bottom"  # Anchor legend to the bottom
                        )
        )
        context['pie_type'] = plotly.offline.plot(fig, output_type='div')

    # Create pie chart by relevance
        pie_essential_df = pd.DataFrame(data = {'values': [sm.median_total_essential, sm.median_total_nonessential],
                                                'labels': ['Relevant', 'Irrelevant']})
        hover_text_template = f"<b>%{{label}}</b>: %{{value:.1f}} mins out of {(sm.median_total_essential + sm.median_total_nonessential):.1f} mins"

        # create figure
        fig = go.Figure(data=[go.Pie(labels=pie_essential_df['labels'], 
                                     values=pie_essential_df['values'], 
                                     hovertemplate=hover_text_template,
                                     marker=dict(colors=['#cccccc', '#f76565']))])
        fig.update_layout(
            title="Relevance",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            #showlegend=False,
            width=450,  # Specify the width
            height=560,  # Specify the height
            font=dict(size=15),
            legend=dict(orientation="h",  # Set legend orientation to horizontal
                        yanchor="bottom"  # Anchor legend to the bottom
                        )
        )
        context['pie_essential'] = plotly.offline.plot(fig, output_type='div')

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/standard.html', context) # pass dictionary

## ----------------------------------------------------------------------------
## Gamma Plot ## --------------------------------------------------------------
## ----------------------------------------------------------------------------
def gamma_dist(request):

    # create context dictionary
    context = {'lower': 0.9,
               'upper': 1.1}

    if request.method == 'POST':
        # Retrieve numbers from the form
        context['lower'] = float(request.POST.get('lower', 0))
        context['upper'] = float(request.POST.get('upper', 0))

        # Create pie chart by type
        out = ed.plot_gamma_distribution(context['lower'] , context['upper'] )
        context['pdf'] = plotly.offline.plot(out, output_type='div')

    # Pass the context dict to be rendered in the html file
    return render(request, 'ed/gamma_dist.html', context) # pass dictionary