import re

from django.core.validators import _lazy_re_compile, RegexValidator
from django.utils.translation import ugettext_lazy as _


def str_list_validator(
    sep=',', message=None, code='invalid', allow_negative=False
):
    regexp = _lazy_re_compile(r'^%(neg)s\w+(?:%(sep)s%(neg)s\w+)*\Z' % {
        'neg': '(-)?' if allow_negative else '',
        'sep': re.escape(sep),
    })
    return RegexValidator(regexp, message=message, code=code)


validate_comma_separated_str_list = str_list_validator(
    message=_('Enter only words separated by commas.'),
)
