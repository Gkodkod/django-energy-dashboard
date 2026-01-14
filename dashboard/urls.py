from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('state/', views.state_analysis, name='state_analysis'),
    path('net-load/', views.net_load_analysis, name='net_load_analysis'),
    path('congestion/', views.congestion_proxy, name='congestion_proxy'),
]
