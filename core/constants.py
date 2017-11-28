ACCOUNT_ACTIVATION_HOURS = 48

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
