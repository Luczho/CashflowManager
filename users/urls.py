from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import SignUpView, MyLoginView

urlpatterns = [
    path('register/', SignUpView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]