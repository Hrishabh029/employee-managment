from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
import uuid

from .models import UserProfile, PasswordResetToken, LoginAttempt
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    UserRegistrationSerializer, 
    PasswordResetSerializer, 
    PasswordResetTokenSerializer,
    LoginAttemptSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling user-related operations
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined']

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        User registration endpoint
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        User login endpoint
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        # Log login attempt
        login_attempt = LoginAttempt.objects.create(
            username=username,
            ip_address=self.get_client_ip(request),
            is_successful=user is not None
        )
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling user profile operations
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['department', 'role']

    def get_queryset(self):
        """
        Customize queryset based on user role
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

class PasswordResetViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling password reset operations
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        """
        Request password reset token
        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate reset token
            token = str(uuid.uuid4())
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
            
            # Send reset email
            reset_url = f"https://yourfrontend.com/reset-password?token={token}"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                'noreply@yourcompany.com',
                [email],
                fail_silently=False,
            )
            
            return Response({'detail': 'Password reset link sent'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """
        Reset password using token
        """
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token, 
                is_used=False, 
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        reset_token.is_used = True
        reset_token.save()
        
        return Response({'detail': 'Password reset successful'})
