from django.urls import path
from . import views

urlpatterns = [
    path('locate_numbers', views.PhoneApiView.as_view()),
]