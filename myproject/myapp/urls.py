from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('healthinsights/', views.healthinsights, name='healthinsights'),
    path('wellnesstracking/', views.wellnesstracking, name='wellnesstracking'),
]
