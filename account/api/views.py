from django.contrib.auth.views import (
    INTERNAL_RESET_URL_TOKEN, INTERNAL_RESET_SESSION_TOKEN
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from . import filters, serializers
from crmplus.api.mixins import CompanyQuerySetMixin
from account.models import Notification, User


class NotificationViewSet(CompanyQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    filter_class = filters.NotificationFilterSet
    model = Notification
    queryset = Notification.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            user=self.request.user
        )


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    model = User
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.UserCreateSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return serializers.UserUpdateSerializer
        elif self.request.method == 'GET':
            return serializers.UserDetailSerializer

    @action(
        detail=False,
        methods=['post'],
        url_path='password-change',
        url_name='password_change'
    )
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

    def get(self, request):
        return Response(
            '', status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

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
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
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
