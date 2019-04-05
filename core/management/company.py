"""
Creates the default Company object.
"""

from django.apps import apps as global_apps
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections, router


def create_default_company(
    app_config, verbosity=2, interactive=True,
    using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs
):
    try:
        Company = apps.get_model('core', 'Company')
        User = apps.get_model('core', 'User')
    except LookupError:
        return

    if not router.allow_migrate_model(using, Company):
        return

    if not router.allow_migrate_model(using, User):
        return

    if not Company.objects.using(using).exists():
        # The default settings set COMPANY_ID = 1, and some tests in Django's
        # test suite rely on this value. However, if database sequences are
        # reused (e.g. in the test suite after flush/syncdb), it isn't
        # #guaranteed that the next id will be 1, so we coerce it. See #15573
        # # and #16353. This can also crop up outside of tests - see #15346.
        if verbosity >= 2:
            print("Creating example.com Company and admin User objects")
        User(
            pk=1,
            username="admin",
            email="example@example.com",
            is_superuser=True,
            is_staff=True,
            password=make_password('admin')
        ).save(using=using)
        Company(
            pk=getattr(settings, 'COMPANY_ID', 1),
            user_id=1,
            domain="example.com",
            name="example.com",
            email="example@example.com"
        ).save(using=using)

        # We set an explicit pk instead of relying on auto-incrementation,
        # so we need to reset the database sequence. See #17415.
        sequence_sql = connections[using].ops.sequence_reset_sql(no_style(), [
                                                                 Company])
        if sequence_sql:
            if verbosity >= 2:
                print("Resetting sequence")
            with connections[using].cursor() as cursor:
                for command in sequence_sql:
                    cursor.execute(command)
