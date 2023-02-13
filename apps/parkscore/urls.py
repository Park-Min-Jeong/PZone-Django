from django.urls import path
from apps.parkscore.views import *

app_name = "parkscore"

urlpatterns = [
	path('score/', score, name="score"),
	path('update/', update, name="update"),
	# path('photo/',forbidden_location,name="photo")
]