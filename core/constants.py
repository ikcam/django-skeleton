from django.utils.translation import ugettext_lazy as _

ACCOUNT_ACTIVATION_HOURS = 48

ACTIONS = {
    'add': {
        'title': _("Add"),
        'level': 'primary',
        'icon': 'plus',
        'permission_prefix': 'add',
    },
    'change': {
        'title': _("Change"),
        'level': 'success',
        'icon': 'pencil',
        'permission_prefix': 'change',
    },
    'delete': {
        'title': _("Delete"),
        'level': 'danger',
        'icon': 'trash',
        'permission_prefix': 'delete',
    },
    'remove': {
        'title': _("Remove"),
        'level': 'danger',
        'icon': 'remove',
        'permission_prefix': 'remove',
    },
    'send': {
        'title': _("Send"),
        'level': 'info',
        'icon': 'envelope',
        'permission_prefix': 'send',
    },
}

CICLE_DAY = 'day'
CICLE_WEEK = 'week'
CICLE_MONTH = 'month'
CICLE_YEAR = 'year'

DIRECTION_OUTBOUND = 'outbound'
DIRECTION_INBOUND = 'inbound'

EVENT_TASK = 'task'
EVENT_APPOINTMENT = 'appointment'
EVENT_CALL = 'call'
EVENT_JOB_START = 'job-start'
EVENT_PRIVATE = 'private'

EVENT_TASK_COLOR = '#641E16'
EVENT_APPOINTMENT_COLOR = '#512E5F'
EVENT_CALL_COLOR = '#154360'
EVENT_JOB_START_COLOR = '#0E6251'
EVENT_PRIVATE_COLOR = '#145A32'

GRACE_DAYS = 7

HREF_REGEX = r'href=(["\'])(.*?)\1'

LEVEL_ERROR = 'error'
LEVEL_INFO = 'info'
LEVEL_SUCCESS = 'success'
LEVEL_WARNING = 'warning'

NOTIFY_0 = 0
NOTIFY_10 = 10
NOTIFY_30 = 30
NOTIFY_60 = 60
NOTIFY_1440 = 24

PIXEL_GIF_DATA = """
R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7
""".strip()

RECURRING_CICLE = CICLE_MONTH
RECURRING_FEE = 50

URL_REGEX = (
    r'(\(.*?)?\b((?:https?|ftp|file):\/\/'
    r'[-a-z0-9+&@#\/%?=~_()|!:,.;]*[-a-z0-9+&@#\/%=~_()|])'
)
