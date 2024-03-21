from django.urls import path
from ed import views

urlpatterns = [
    path("", views.home, name="home"),
    path("teams/", views.teams, name = "teams"),
    path("teams_stochastic/", views.teams_stochastic, name = "ts")
]