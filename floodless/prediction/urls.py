from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_disaster, name='predict_disaster'),
]