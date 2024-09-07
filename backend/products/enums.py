from enum import Enum
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class DocumentEventsEnum(str, Enum):
    NOTIFY_SUCCESS = "notify_success"
    NOTIFY_FAILURE = "notify_failure"
