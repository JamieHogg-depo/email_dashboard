from django.urls import path
from ed import views

urlpatterns = [
    path("", views.home, name="home")
]