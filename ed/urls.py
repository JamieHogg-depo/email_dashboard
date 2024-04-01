from django.urls import path
from ed import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("basic/", views.basic, name = "basic"),
    path("gamma_dist/", views.gamma_dist, name = "gamma_dist"),
    path("intermediate/", views.intermediate, name = "intermediate")
]