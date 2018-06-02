from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from .models import User

from dal import autocomplete


class GroupAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.has_perm('auth.view_group'):
            return Group.objects.none()

        qs = Group.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PermissionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if (
            not self.request.user.is_authenticated or
            not self.request.user.company
        ):
            return Permission.objects.none()

        qs = Permission.objects.all().exclude(
            content_type__app_label__in=(
                'admin', 'authtoken', 'contenttypes', 'sessions',
            )
        ).exclude(
            content_type__model__in=(
                'colaborator', 'group', 'logentry', 'payment', 'permission',
                'profile',
            )
        ).exclude(
            codename__in=(
                'add_invoice', 'change_invoice', 'delete_invoice',
                'add_company', 'delete_company'
            )
        )

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(content_type__app_label__icontains=self.q) |
                Q(content_type__model__icontains=self.q)
            )

        return qs


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if (
            not self.request.user.is_authenticated or
            not self.request.user.company
        ):
            return User.objects.none()

        qs = User.objects.filter(
            profile__companies=self.request.user.company
        ).order_by('username')

        if self.q:
            qs = qs.filter(
                Q(username__istartswith=self.q) |
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q)
            )

        return qs


class UserOtherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if (
            not self.request.user.is_authenticated or
            not self.request.user.company
        ):
            return User.objects.none()

        qs = User.objects.filter(
            profile__companies=self.request.user.company
        ).exclude(pk=self.request.user.pk).order_by('username')

        if self.q:
            qs = qs.filter(
                Q(username__istartswith=self.q) |
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q)
            )

        return qs
