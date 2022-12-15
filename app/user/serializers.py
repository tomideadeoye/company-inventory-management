from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email, EmailNotValidError
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Token, User
from .utils import ValidatePassword
from .tasks import send_new_user_email, send_login_email


class BasicUserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'fullname', 'email', 'role', 'phone',
                  'is_active', 'status']

    @staticmethod
    def get_status(obj: User) -> str:
        return obj.status


class ListUserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'fullname', 'is_active', 'email', 'role', 'workspace', 'mac_address', 'location',
                    'position', 'image', 'verified', 'last_login', 'created_at', 'phone', 'status']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        from workspaces.serializers import WorkSpaceSerializer
        data['workspace'] = WorkSpaceSerializer(instance=instance.workspace, many=True).data
        return data

    @staticmethod
    def get_status(obj: User) -> str:
        return obj.status


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'fullname', 'role', 'workspace')

    def validate(self, attrs):
        email = attrs.get('email')
        valid_domains = ['dukka.com', 'dipfellows.org']
        for domain in valid_domains:
            if email.split('@')[1] not in valid_domains:
                raise serializers.ValidationError({'email': 'not a valid email address'})
        role = attrs['role']
        creator = self.context['request'].user
        if role == 'SUPER_ADMIN':
            raise serializers.ValidationError({'role': 'Invalid role selected'})

        if role == 'HYBRID_ADMIN' and creator.role not in ['SUPER_ADMIN', 'HYBRID_ADMIN']:
            raise serializers.ValidationError({'role': 'you are not authorized to create user with this role'})
        if role == 'TMS_ADMIN' and creator.role not in ['SUPER_ADMIN', 'HYBRID_ADMIN', 'TMS_ADMIN']:
            raise serializers.ValidationError({'role': 'you are not authorized to create user with this role'})
        if role == 'AMS_ADMIN' and creator.role not in ['SUPER_ADMIN', 'HYBRID_ADMIN', 'AMS_ADMIN']:
            raise serializers.ValidationError({'role': 'you are not authorized to create user with this role'})
        if email:
            email = attrs['email'].lower().strip()
            if get_user_model().objects.filter(email=email).exists():
                raise serializers.ValidationError('Email already exists')
            try:
                valid = validate_email(attrs['email'])
                attrs['email'] = valid.email
                return super().validate(attrs)
            except EmailNotValidError as e:
                raise serializers.ValidationError(e)
        return super().validate(attrs)

    def create(self, validated_data):
        default_password=get_random_string(8)
        workspace = validated_data.pop('workspace')
        # print(workspace)
        user = User.objects.create_user(**validated_data, password=default_password)
        user.workspace.set(workspace)
        token, _ = Token.objects.update_or_create(
            user=user, token_type='ACCOUNT_VERIFICATION',
            defaults={'user': user, 'token_type': 'ACCOUNT_VERIFICATION', 'token': get_random_string(120)})
        user_data = {'id': user.id, 'email': user.email, 'fullname': user.fullname, 'password': default_password,
                     'url': f"{settings.CLIENT_URL}/signin/?token={token.token}"}    
        print(token.token)
        send_new_user_email.delay(user_data)
        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if validated_data.get('password', False):
            instance.set_password(validated_data.get('password'))
            instance.save()
        return instance


class ResendTokenSerializer(serializers.Serializer):
    """Serializer for resending token"""
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        user = get_user_model().objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('User does not exists')
        if user.verified:
            raise serializers.ValidationError({'user': 'cannot resend token to a user who status is not pending '})
        return super().validate(attrs)

    def create(self, validated_data):
        email = validated_data['email']
        user = get_user_model().objects.filter(email=email).first()
        token = Token.objects.filter(user=user)
        if token.exists():
            token.delete()
        token = Token.objects.create(user=user, token=get_random_string(120),
                                     token_type='ACCOUNT_VERIFICATION')
        user_data = {'id': user.id, 'email': user.email, 'fullname': user.fullname,
                     'url': f"{settings.CLIENT_URL}/verify-user/?token={token.token}"}
        send_new_user_email.delay(user_data)
        return user


class SigninEmailSerializer(serializers.Serializer):
    """Serializer for accepting login email"""
    email = serializers.EmailField()
    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        user = get_user_model().objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('User does not exists')
        email_data = {'id': user.id, 'email': user.email,
                     'url': f"{settings.CLIENT_URL}/login-password/?email={user.email}"}    
        send_login_email.delay(email_data)    
        return super().validate(attrs)


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):


    @classmethod
    def get_token(cls, user):
        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                _('Account archived.'), code='authentication')
        if not user.verified:
            raise exceptions.AuthenticationFailed(
                _('Account not yet verified.'), code='authentication')
        token = super().get_token(user)
        # Add custom claims
        token.id = user.id
        token['email'] = user.email
        token['role'] = user.role
        token['fullname'] = user.fullname
        workspaces = user.workspace.all() 
        for workspace in workspaces:
            token['workspace'] = str(workspace.id) if workspace else None

        user.save_last_login()
        return token


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            user = authenticate(
                request=self.context.get('request'),
                username=email.lower().strip(),
                password=password
            )

        if not user:
            msg = _('Invalid email or password')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs


class VerifyTokenSerializer(serializers.Serializer):
    """Serializer for token verification"""
    token = serializers.CharField(required=True)


class InitializePasswordResetSerializer(serializers.Serializer):
    """Serializer for sending password reset email to the user"""
    email = serializers.CharField(required=True)


class CreatePasswordSerializer(serializers.Serializer):
    """Serializer for password change on reset"""
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        ValidatePassword(attrs['password']).validate()
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({'password': 'The two password fields must match.'})
        return attrs


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        
        fields = ['email', 'role', 'position', 'workspace', 'mac_address']
        extra_kwargs = {
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True}
        }


class UpdateUserStatusSerializer(serializers.Serializer):
    user_status = serializers.ChoiceField(choices=(('ACTIVATE', 'ACTIVATE'),
                                              ('ARCHIVE', 'ARCHIVE')))

    def validate(self, attrs):
        user = self.instance
        admin = self.context['SUPER_ADMIN']
        user_status = attrs['user_status']
        
        if user_status == 'ACTIVATE' and user.is_active:
            raise serializers.ValidationError(
                {'status': 'can only activate an archived user'})
        elif user_status == 'ARCHIVE' and not user.is_active:
            raise serializers.ValidationError(
                {'status': 'can only archive an active user'})

        return attrs

    def update(self, instance, validated_data):
        user_status = True if self.validated_data['user_status'] == 'ACTIVATE' else False
        instance.is_active = user_status
        instance.save()
        return instance
