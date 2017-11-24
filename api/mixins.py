from django.core.exceptions import (
    ImproperlyConfigured, ObjectDoesNotExist, PermissionDenied
)
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response


class CompanyRequiredMixin:
    company = None
    company_field = 'company'
    permissions_required = None

    def get_company_field(self):
        return self.company_field

    def get_permissions_required(self):
        return self.permissions_required

    def handle_no_permission(self, msg=None):
        raise PermissionDenied(msg)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.company = request.user.profile.company

        if not self.company.is_active:
            return self.handle_no_permission()

        permissions_required = self.get_permissions_required()

        if permissions_required and isinstance(permissions_required, tuple):
            if not request.user.has_company_perms(permissions_required):
                return self.handle_no_permission()
        elif permissions_required:
            if not request.user.has_company_perm(permissions_required):
                return self.handle_no_permission()


class CompanyQuerySetMixin(CompanyRequiredMixin):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{
            self.get_company_field(): self.company
        })


class CompanyCreateMixin(CompanyRequiredMixin):
    def get_perform_create_kwargs(self):
        try:
            kwargs = super().get_perform_create_kwargs()
        except Exception:
            kwargs = {}

        kwargs.update({
            'company': self.request.user.profile.company,
        })

        return kwargs

    def perform_create(self, serializer):
        serializer.perform_create(**self.get_perform_create_kwargs())


class NestedReadOnlyViewset(CompanyRequiredMixin):
    parent_relation_field = None

    def get_parent(self, parent_pk):
        queryset = self.get_parent_model().objects.filter(
            **self.get_parent_kwargs()
        )
        try:
            return queryset.get(pk=parent_pk)
        except ObjectDoesNotExist:
            return self.handle_no_permission()

    def get_parent_kwargs(self):
        kwargs = {
            self.get_company_field(): self.company,
        }
        return kwargs

    def get_parent_model(self):
        if not self.parent_model:
            raise ImproperlyConfigured("You must set the `parent_model`")
        return self.parent_model

    def get_parent_relation_field(self):
        if self.parent_relation_field:
            return self.parent_relation_field

        return self.request.resolver_match.url_name.split('_')[0]

    def list(self, request, parent_pk=None):
        queryset = self.filter_queryset(self.get_queryset())

        if parent_pk:
            queryset = queryset.filter(**{
                self.get_parent_relation_field(): parent_pk
            })

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, parent_pk=None):
        queryset = self.get_queryset()

        if parent_pk:
            queryset = queryset.filter(**{
                self.get_parent_relation_field(): parent_pk,
            })

        instance = get_object_or_404(queryset, pk=pk)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class NestedViewset(NestedReadOnlyViewset):
    parent_relation_field = None
    parent_company_field = 'company'

    def create(self, request, parent_pk=None, *args, **kwargs):
        parent = self.get_parent(parent_pk=parent_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, parent)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_perform_create_kwargs(self, parent):
        try:
            kwargs = super().get_perform_create_kwargs()
        except Exception:
            kwargs = {}

        kwargs = {
            self.get_parent_relation_field(): parent
        }

        return kwargs

    def perform_create(self, serializer, parent):
        kwargs = self.get_perform_create_kwargs(parent)
        serializer.save(**kwargs)


class UserCreateMixin(CompanyRequiredMixin):
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


class UserQuerySetMixin(CompanyQuerySetMixin):
    user_field = 'user'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{
            self.get_user_field(): self.request.user
        })

    def get_user_field(self):
        return self.user_field
