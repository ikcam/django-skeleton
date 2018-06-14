from django.core.validators import EMPTY_VALUES


def phone_clean(phone_number=None):
    if phone_number in EMPTY_VALUES:
        return None

    phone_number = '%s' % phone_number
    phone_number = phone_number \
        .replace(' ', '') \
        .replace('/', '') \
        .replace('-', '') \
        .replace('(', '') \
        .replace(')', '') \
        .strip()

    if '+1' in phone_number:
        return phone_number
    else:
        return '+1{}'.format(phone_number)
