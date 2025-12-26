from django.urls import path
from . import auth_views

urlpatterns = [
    path('register/', auth_views.register, name='register'),
    path('profile/', auth_views.profile, name='profile'),
]

