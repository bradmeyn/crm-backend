from django.urls import path
from .views import BusinessRegistrationView, UserCreateView, CustomTokenObtainPairView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Public auth endpoints
    path('auth/register/', BusinessRegistrationView.as_view(), name='register'), 
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Protected endpoints
    path('users/', UserCreateView.as_view(), name='create_user'),
    path('me/', UserProfileView.as_view(), name='user_profile'), 
]