from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


User = get_user_model()


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
