from django.urls import path
from ed import views
from django.http import HttpResponse

def blank_favicon(request):
    return HttpResponse("", content_type="image/x-icon")

urlpatterns = [
    path('favicon.ico', blank_favicon),
    path("", views.landing, name="landing"),
    path("basic/", views.basic, name = "basic"),
    path("gamma_dist/", views.gamma_dist, name = "gamma_dist"),
    path("intermediate/", views.intermediate, name = "intermediate")
]