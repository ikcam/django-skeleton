from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext_lazy as _


from rest_framework import serializers

from account.models import Profile
from core.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = Company


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(
        self,
        request,
        email_template_name='registration/password_email.html',
        html_email_template_name='registration/password_email_html.html',
        subject_template_name='registration/password_subject.txt',
        password_reset_form=PasswordResetForm,
        token_generator=default_token_generator,
        post_reset_redirect=None,
        from_email=None,
        extra_context=None,
        extra_email_context=None
    ):
        form = password_reset_form(self.data)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
                'extra_email_context': extra_email_context,
            }
            form.save(**opts)
            return True
        return False


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = (
            'user', 'companies', 'activation_key', 'date_key_expiration'
        )
        model = Profile


class ProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'profile'
        )
        model = User


class SetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data

    def validate_password2(self, data):
        try:
            password_validation.validate_password(data)
        except serializers.ValidationError as error:
            raise serializers.ValidationError(error)
        return data

    def save(self):
        password = self.validated_data["new_password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email'
        )
        model = User


class SignUpSerializer(serializers.ModelSerializer):
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
        try:
            password_validation.validate_password(data)
        except serializers.ValidationError as error:
            raise serializers.ValidationError(error)
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
