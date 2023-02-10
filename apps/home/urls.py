from django.urls import path
from apps.home.views import index

app_name = "home"

urlpatterns = [
    path('', index, name="home"),
]