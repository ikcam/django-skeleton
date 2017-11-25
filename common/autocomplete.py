from dal import autocomplete
from queryset_sequence import QuerySetSequence

from core.mixins import CompanyRequiredMixin
from common.models import Message


class ModelAutocomplete(
    CompanyRequiredMixin, autocomplete.Select2QuerySetSequenceView
):
    def get_queryset(self):
        messages = Message.objects.filter(company=self.company)

        if self.q:
            messages = messages.filter(to_email__icontains=self.q)

        qs = QuerySetSequence(messages)
        qs = self.mixup_querysets(qs)

        return qs
