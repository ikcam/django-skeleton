from django.contrib.auth.backends import ModelBackend
from .models import User


class AuthenticationBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            # This is where the magic happens
            return User.objects.select_related(
                'company',
            ).get(
                pk=user_id
            )
        except User.DoesNotExist:
            return None
