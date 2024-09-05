from enum import Enum

class DocumentEventsEnum(str, Enum):
    NOTIFY_SUCCESS = "notify_success"
    NOTIFY_FAILURE = "notify_failure"
