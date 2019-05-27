from django.contrib.auth.tokens import PasswordResetTokenGenerator


class InviteSendTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        login_timestamp = (
            ''
            if user.date_creation is None
            else user.date_creation.replace(microsecond=0, tzinfo=None)
        )
        return (
            str(user.pk) + user.email + str(login_timestamp) + str(timestamp)
        )


default_token_generator = InviteSendTokenGenerator()
