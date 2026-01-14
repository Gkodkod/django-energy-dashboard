from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('state/', views.state_analysis, name='state_analysis'),
]
