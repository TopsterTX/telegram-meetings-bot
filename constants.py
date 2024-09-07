NOTIFY_PREFIX = "notify"
NOTIFY_ACCEPT = "accept"
NOTIFY_REJECT = "reject"
NOTIFY_LATE = "late"
MEETING_READY = "meeting_ready"
MEETING_CANCEL = "meeting_cancel"
SUCCESS_REGISTRATION = "accept_write_user_data"
REJECT_REGISTRATION = "reject_write_user_data"
SELECT_PARTICIPANTS_PREFIX = "select"
SELECT_APPROVE = f"approve_{SELECT_PARTICIPANTS_PREFIX}"
UNSELECT_PARTICIPANTS_PREFIX = "unselect"

# Commands
CREATE_MEETING = "create_meeting"
START = "start"
LIST_FRIENDS = "list_friends"
CANCEL_COMMAND = "cancel"

# Meeting statuses
CREATING = "creating"
EDITING = "editing"
CANCEL = "cancel"
REJECT = "reject"
PROCESSING = "processing"
EXPIRED = "expired"
MEETING_STATUSES = [CREATING, EDITING, CANCEL, REJECT, PROCESSING, EXPIRED]

# DB constants
DEFAULT_ERROR = "default_error"
RECORD_ALREADY_EXIST = "record_already_exist"
