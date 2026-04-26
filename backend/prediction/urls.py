from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict, name='api_predict'),
    path('history/', views.history, name='api_history'),
    path('analytics/', views.analytics, name='api_analytics'),
    path('statistics/', views.statistics, name='api_statistics'),
]
