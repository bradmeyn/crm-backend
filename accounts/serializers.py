from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Business
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'business', 'phone']

class RegisterSerializer(serializers.ModelSerializer):
    """For initial business signup - creates both business and admin user"""
    business_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True) 

    class Meta:
        model = User
        fields = ['business_name', 'email', 'password', 'first_name', 
                 'last_name', 'phone']

    def validate_email(self, value):
        """Check if email is already taken"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        password = validated_data.pop('password')
        
        # Create business first
        business = Business.objects.create(name=business_name)
        
        # Create admin user
        user = User.objects.create(
            business=business,
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        return user

class UserCreateSerializer(serializers.ModelSerializer):
    """For creating additional users within an existing business"""
    password = serializers.CharField(write_only=True, min_length=8) 
    business = BusinessSerializer(read_only=True)
    business_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 
                 'business', 'business_id', 'phone']
        read_only_fields = ['id']

    def validate_email(self, value):
        """Check if email is already taken"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_business_id(self, value):
        """Check if business exists"""
        if not Business.objects.filter(id=value).exists():
            raise serializers.ValidationError("Business not found.")
        return value

    def create(self, validated_data):
        business_id = validated_data.pop('business_id')
        password = validated_data.pop('password')
        business = Business.objects.get(id=business_id)
        
        user = User.objects.create(
            business=business,
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to the response
        user_serializer = UserSerializer(self.user)
        data['user'] = user_serializer.data
        
        return data