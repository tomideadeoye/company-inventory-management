from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import UserFilter
from .models import User, Token
from .serializers import (CreateUserSerializer, ListUserSerializer, AuthTokenSerializer,
                          CustomObtainTokenPairSerializer, VerifyTokenSerializer,
                          CreatePasswordSerializer, SigninEmailSerializer,
                          InitializePasswordResetSerializer, UpdateUserStatusSerializer, ResendTokenSerializer, UpdateUserSerializer)
from .tasks import send_password_reset_email
from .permissions import IsAmsAdmin, IsSuperAdmin, IsHybridAdmin, IsTmsAdmin


class AuthViewSets(viewsets.GenericViewSet, viewsets.generics.RetrieveUpdateAPIView,
                        viewsets.generics.ListAPIView, viewsets.generics.DestroyAPIView):
    """User ViewSets"""
    queryset = get_user_model().objects.all()
    serializer_class = ListUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['email', 'fullname', 'phone']
    ordering_fields = ['created_at', 'last_login', 'email', 'fullname', 'phone']

    def get_serializer_class(self):
        if self.action == 'create_password':
            return CreatePasswordSerializer
        elif self.action == 'initialize_reset':
            return InitializePasswordResetSerializer
        elif self.action == 'verify_token':
            return VerifyTokenSerializer
        elif self.action in ['create', 'invite_user']:
            return CreateUserSerializer
        elif self.action == 'partial_update':
            return UpdateUserSerializer    
        return super().get_serializer_class()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ['create_password', 'initialize_reset', 'verify_token', 'retrieve', 'list']:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(methods=['POST'], detail=False, serializer_class=CreateUserSerializer,
            permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin], url_path='invite-user')
    def invite_user(self, request, pk=None):
        """This endpoint invites new user by admin"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, serializer_class=ResendTokenSerializer,
            permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin], url_path='resend-token')
    def resend_token(self, request, pk=None):
        """This endpoint resends token """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, serializer_class=VerifyTokenSerializer, url_path='verify-token')
    def verify_token(self, request, pk=None):
        """This endpoint verifies token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = Token.objects.filter(
                token=request.data.get('token')).first()
            if token and token.is_valid():
                token.verify_user()
                return Response({'success': True, 'valid': True}, status=status.HTTP_200_OK)
            return Response({'success': True, 'valid': False}, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, serializer_class=InitializePasswordResetSerializer,
            url_path='reset-password')
    def initialize_reset(self, request, pk=None):
        """This endpoint initializes password reset by sending password reset email to user"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = request.data['email'].lower().strip()
            user = get_user_model().objects.filter(email=email, is_active=True).first()
            if not user:
                return Response({'success': False, 'message': 'Invalid credentials'},
                                status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.update_or_create(user=user, token_type='PASSWORD_RESET', 
            defaults={
                'user': user, 'token_type': 'PASSWORD_RESET',
                'token': get_random_string(120),
                },
            )
            email_data = {'fullname': user.fullname,
                          'email': user.email,
                          'token': token.token,
                          'url': f"{settings.CLIENT_URL}/passwordreset/?token={token.token}",
            }
            send_password_reset_email.delay(email_data)
            print(token.token)
            return Response({'success': True, 'message': 'Email successfully sent to registered email'},
                            status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False, serializer_class=CreatePasswordSerializer, url_path='change-password')
    def create_password(self, request, pk=None):
        """Create a new password given the reset token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = Token.objects.filter(
                token=request.data['token']).first()
            if not token or not token.is_valid():
                return Response({'success': False, 'errors': 'Invalid token specified'},
                                status=status.HTTP_400_BAD_REQUEST)
            token.reset_user_password(request.data['password'])
            token.verify_user()
            token.delete()
            return Response({'success': True, 'message': 'Password successfully reset'}, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
        serializer_class=UpdateUserStatusSerializer,
        url_path="update-status",
    )
    def update_user_status(self, request, pk=None):
        user = self.get_object()
        serializer = self.serializer_class(data=request.data, instance=user,
                                         context={'SUPER_ADMIN': self.request.user}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, 'message': 'status updated successfully'}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, serializer_class=SigninEmailSerializer,
            permission_classes=[AllowAny], url_path='login-email')
    def login_email(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with email and password"""
    serializer_class = CustomObtainTokenPairSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'created': created, 'role': user.role}, status=status.HTTP_200_OK)
