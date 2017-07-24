from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator

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
    password_confirm = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return data


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
        )
        model = User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email'
        )
        model = User


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        fields = (
            'username', 'first_name', 'last_name', 'password1',
            'password2', 'email'
        )
        model = User

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def validate_email(self, data):
        exists = User.objects.filter(email=data).exists()
        if exists:
            raise serializers.ValidationError(
                "Email already in use by another user."
            )
        return data
