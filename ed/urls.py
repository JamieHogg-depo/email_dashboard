from django.urls import path
from ed import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("basic/", views.basic, name = "basic"),
    path("teams/", views.teams, name = "teams"),
    path("basic_nouncertainty/", views.basic_nouncertainty, name = "basic_nouncertainty"),
    path("gamma_dist/", views.gamma_dist, name = "gamma_dist"),
    path("teams_stochastic/", views.teams_stochastic, name = "teams_stochastic")
]