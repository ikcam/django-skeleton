from django.contrib.auth import password_validation
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.api.serializers import ActionSerializer
from core.models import (
    Colaborator, Company, Event, Link, Notification, Message, User, Visit
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'switch_url')
        model = Company


class ColaboratorSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        fields = ('company', 'date_joined', 'is_active')
        model = Colaborator


class EventModelSerializer(ActionSerializer):
    user = serializers.StringRelatedField()
    type_color = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'user', 'share_with', 'date', 'date_creation',
            'date_start', 'date_finish', 'subject', 'content', 'type',
            'type_color', 'is_public', 'action_list'
        )
        model = Event

    def get_type_color(self, obj):
        return obj.get_type_color()


class LinkModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'date_creation', 'message', 'user', 'token', 'destination',
            'is_open', 'total_visits', 'action_list'
        )
        model = Link


class MessageModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'contenttype', 'model', 'status', 'direction',
            'date_creation', 'date_modification', 'from_email', 'from_name',
            'to_email', 'to_email_cc', 'reply_to_email', 'subject', 'content',
            'action_list'
        )
        model = Message


class NotificationModelSerializer(ActionSerializer):
    model = serializers.StringRelatedField()

    class Meta:
        exclude = (
            'contenttype', 'company', 'destination', 'is_active', 'object_id',
            'user'
        )
        model = Notification


class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        fields = (
            'username', 'password1', 'password2', 'first_name', 'last_name',
            'email'
        )
        model = User

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )

        return data

    def validate_password2(self, data):
        password_validation.validate_password(data)
        return data

    def validate_email(self, data):
        exists = User.objects.filter(email=data).exists()
        if exists:
            raise serializers.ValidationError(
                _("A user with that email already exists.")
            )
        return data

    def save(self):
        user = super().save()
        user.set_password(self.validated_data["password1"])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    colaborator_set = ColaboratorSerializer(read_only=True, many=True)

    class Meta:
        fields = (
            'username', 'first_name', 'last_name', 'email', 'nav_expanded',
            'language', 'timezone', 'photo', 'company', 'colaborator_set',
        )
        model = User


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name', 'last_name', 'language', 'photo', 'timezone',
            'nav_expanded',
        )
        model = User


class VisitModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'date_creation', 'link', 'ip_address', 'action_list'
        )
        model = Visit
