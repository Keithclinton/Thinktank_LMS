from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('token/', views.login, name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile - RESTful design
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),  # GET and PUT
    path('user/change-password/', views.change_password, name='change_password'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
]
