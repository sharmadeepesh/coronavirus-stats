from django.urls import path
from . import views

urlpatterns = [
	path('country/<str:country_name>', views.country, name="country"),
	path('',views.index, name="homepage"),
]