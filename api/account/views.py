from django.contrib.auth.models import User

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, list_route, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.mixins import (
    CompanyQuerySetMixin
)
from . import serializers


@api_view(['POST'])
@permission_classes((AllowAny, ))
def password_reset(request):
    serializer_class = serializers.PasswordResetSerializer
    serializer = serializer_class(data=request.data)
    if serializer.is_valid():
        serializer.save(request=request)
        return Response({'status': 'email reset send'})
    else:
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes((AllowAny, ))
def signup(request):
    serializer_class = serializers.SignupSerializer
    serializer = serializer_class(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class MeViewSet(viewsets.ViewSet):
    queryset = User.objects.all()

    def list(self, request):
        serializer = serializers.MeSerializer(request.user)
        return Response(serializer.data)

    @list_route(methods=['get', 'post', 'patch'])
    def profile(self, request):
        if request.method in ['PATCH', 'POST']:
            serializer = serializers.ProfileSerializer(
                request.user.profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = serializers.ProfileSerializer(
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


class UserViewSet(
    CompanyQuerySetMixin, viewsets.ReadOnlyModelViewSet
):
    company_field = 'profile__companies'
    model = User
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
