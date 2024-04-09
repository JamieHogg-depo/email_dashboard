from django.urls import path
from ed import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("standard/", views.standard, name = "standard"),
    path("gamma_dist/", views.gamma_dist, name = "gamma_dist"),
    path("advanced/", views.advanced, name = "advanced")
]