from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from rest_framework import mixins, viewsets


class CompanyCreateMixin:
    company_field = 'company'

    def get_company_field(self):
        return self.company_field

    def get_perform_create_kwargs(self):
        try:
            kwargs = super().get_perform_create_kwargs()
        except AttributeError:
            kwargs = {}

        kwargs.update({
            self.get_company_field(): self.request.company,
        })

        return kwargs

    def perform_create(self, serializer):
        serializer.save(**self.get_perform_create_kwargs())


class CompanyReadOnlyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    company = None
    company_field = 'company'
    bypass_permissions = False
    related_properties = None
    prefetch_properties = None

    def get_bypass_permissions(self):
        return self.bypass_permissions

    def get_company_field(self):
        return self.company_field

    def get_permission_name(self, action):
        return '{app_name}:{action}_{model_name}'.format(
            action=action,
            app_name=self.model._meta.app_label,
            model_name=self.model.__name__.lower(),
        )

    def get_prefetch_properties(self):
        return self.related_properties

    def get_related_properties(self):
        return self.related_properties

    def get_queryset(self):
        if not self.request.company:
            raise Exception(_("Company must be set."))

        qs = super().get_queryset()
        qs = qs.filter(**{
            self.get_company_field(): self.request.company
        })

        related_properties = self.get_related_properties()
        if related_properties:
            if not isinstance(related_properties, tuple):
                raise Exception("`related_properties` must be a tuple")
            qs = qs.select_related(*related_properties)

        prefetch_properties = self.get_prefetch_properties()
        if prefetch_properties:
            if not isinstance(prefetch_properties, tuple):
                raise Exception("`prefetch_properties` must be a tuple")
            qs = qs.prefetch_related(*prefetch_properties)

        return qs

    def handle_no_permission(self, msg=None):
        raise PermissionDenied(msg)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if not self.request.company.is_active:
            return self.handle_no_permission()

    def list(self, request, *args, **kwargs):
        permission_name = self.get_permission_name('view')

        if (
            not self.get_bypass_permissions() and
            not request.user.has_company_perm(
                self.request.company, permission_name
            )
        ):
            return self.handle_no_permission()

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        permission_name = self.get_permission_name('view')

        if not request.user.has_company_perm(
            self.request.company, permission_name
        ):
            return self.handle_no_permission()

        return super().retrieve(request, *args, **kwargs)


class CompanyViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CompanyReadOnlyViewSet
):
    def create(self, request, *args, **kwargs):
        permission_name = self.get_permission_name('add')

        if not request.user.has_company_perm(permission_name):
            return self.handle_no_permission()

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        permission_name = self.get_permission_name('change')

        if not request.user.has_company_perm(permission_name):
            return self.handle_no_permission()

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        permission_name = self.get_permission_name('delete')

        if not request.user.has_company_perm(permission_name):
            return self.handle_no_permission()

        return super().destroy(request, *args, **kwargs)


class NestedReadOnlyViewset(CompanyReadOnlyViewSet):
    parent = None
    parent_company_field = 'company'
    parent_model = None
    parent_relation_field = None
    parent_lookup_arg = 'parent_pk'
    parent_lookup_field = 'pk'

    def get_parent(self):
        kwargs = self.get_parent_kwargs()

        if kwargs:
            return get_object_or_404(
                self.get_parent_model(), **kwargs
            )
        return None

    def get_parent_kwargs(self):
        try:
            kwargs = {
                self.get_parent_lookup_field(): self.kwargs[
                    self.get_parent_lookup_arg()
                ],
            }
            return kwargs
        except KeyError:
            return None

    def get_parent_lookup_arg(self):
        return self.parent_lookup_arg

    def get_parent_lookup_field(self):
        return self.parent_lookup_field

    def get_parent_model(self):
        return self.parent_model

    def get_parent_relation_field(self):
        if self.parent_relation_field:
            return self.parent_relation_field

        url_name = self.request.resolver_match.url_name

        if '_' in url_name:
            return url_name.split('_')[0]
        return None

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.parent:
            return qs

        return qs.filter(
            **{self.get_parent_relation_field(): self.parent}
        )

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.parent = self.get_parent()


class NestedViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    NestedReadOnlyViewset
):

    def get_perform_create_kwargs(self):
        try:
            kwargs = super().get_perform_create_kwargs()
        except Exception:
            kwargs = {}

        kwargs = {
            self.get_parent_relation_field(): self.parent,
        }

        return kwargs

    def perform_create(self, serializer):
        kwargs = self.get_perform_create_kwargs()
        serializer.save(**kwargs)


class UserCreateMixin:
    user_field = 'user'

    def get_perform_create_kwargs(self):
        try:
            kwargs = super().get_perform_create_kwargs()
        except Exception:
            kwargs = {}

        kwargs.update({
            self.get_user_field(): self.request.user,
        })

        return kwargs

    def get_user_field(self):
        return self.user_field

    def perform_create(self, serializer):
        serializer.perform_create(**self.get_perform_create_kwargs())


class UserQuerySetMixin:
    user_field = 'user'

    def get_queryset(self):
        qs = super().get_queryset()
        permission_name = self.get_permission_name('view_all')

        if self.request.user.has_company_perm(permission_name):
            return qs

        return qs.filter(**{
            self.get_user_field(): self.request.user
        })

    def get_user_field(self):
        return self.user_field
