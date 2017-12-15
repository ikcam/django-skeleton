from django.contrib.auth import get_user_model
from django.contrib.auth.views import (
    INTERNAL_RESET_URL_TOKEN, INTERNAL_RESET_SESSION_TOKEN
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework import generics, permissions, views
from rest_framework.response import Response

from . import serializers


UserModel = get_user_model()


class ProfileViewSet(viewsets.ViewSet):
    queryset = User.objects.all()

    def list(self, request):
        serializer = serializers.ProfileSerializer(request.user)
        return Response(serializer.data)

    @list_route(methods=['get', 'post', 'patch'])
    def profile(self, request):
        if request.method in ['PATCH', 'POST']:
            serializer = serializers.UserProfileSerializer(
                request.user.profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = serializers.UserProfileSerializer(
                request.user.profile
            )

        return Response(serializer.data)

    @list_route(methods=['post'])
    def password_change(self, request):
        serializer_class = serializers.PasswordChangeSerializer
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({'status': 'password set'})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(request=request)
            return Response({'status': 'email reset send'})
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetConfirmView(views.APIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = serializers.SetPasswordSerializer
    token_generator = default_token_generator

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        return user

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])
        self.data_token = None
        self.token = kwargs['token']

        if self.user is not None:
            if self.token == INTERNAL_RESET_URL_TOKEN:
                self.data_token = request.data.get(
                    INTERNAL_RESET_SESSION_TOKEN
                )
                if self.token_generator.check_token(
                    self.user, self.data_token
                ):
                    self.validlink = True
            else:
                if self.token_generator.check_token(self.user, self.token):
                    self.validlink = True

    def get(self, request, *args, **kwargs):
        if not self.validlink:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'token': self.token})

    def post(self, request, *args, **kwargs):
        if not self.validlink:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(user=self.user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    queryset = User.objects.all()
    serializer_class = serializers.SignUpSerializer
