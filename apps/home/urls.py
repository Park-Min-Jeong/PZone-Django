from django.urls import path
from apps.home.views import *

app_name = "home"

urlpatterns = [
    path('', index, name="home"),
    path("error1/", noGPS, name="nogps"),
    path("error2/", notGangNam, name="notgangnam"),
    path("angle/", angle, name="angle")
]