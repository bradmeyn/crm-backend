from rest_framework import status
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserCreateSerializer, RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
import logging

logger = logging.getLogger(__name__)

class BusinessRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                user.is_business_admin = True
                user.save()
                
                refresh = RefreshToken.for_user(user)
                
                logger.info(f"New business registration: {user.email}, business: {user.business.name}")
                
                return Response({
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Registration failed: {str(e)}")
                return Response(
                    {'error': 'Registration failed. Please try again.'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateView(APIView):
    """Protected endpoint for creating additional business users"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user is a business admin
        if not request.user.is_business_admin:
            return Response(
                {'error': 'Only business admins can create users'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user has a business
        if not request.user.business:
            return Response(
                {'error': 'User must belong to a business'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data.copy()
        data['business_id'] = str(request.user.business.id)
        
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user data with tokens"""
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    """Get current user's profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Requires token_blacklist in INSTALLED_APPS
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)