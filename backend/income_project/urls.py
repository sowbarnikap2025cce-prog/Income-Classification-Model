from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Frontend Pages
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('analytics/', TemplateView.as_view(template_name='analytics.html'), name='analytics'),
    path('statistics/', TemplateView.as_view(template_name='statistics.html'), name='statistics'),
    
    # API endpoints
    path('api/', include('users.urls')),
    path('api/', include('prediction.urls')),
]
