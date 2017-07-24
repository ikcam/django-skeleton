from dal import autocomplete

from .models import Role


class RoleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if (
            not self.request.user.is_authenticated or
            not self.request.user.profile.company
        ):
            return Role.objects.none()

        qs = Role.objects.filter(
            company=self.request.user.profile.company,
        )

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
