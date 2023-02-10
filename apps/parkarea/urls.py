from django.urls import path
from apps.parkarea.views import *

app_name = "parkarea"

urlpatterns = [
	path('parkmap/', parkmap, name="parkmap"),
]