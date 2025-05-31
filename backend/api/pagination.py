from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE, PAGE_SIZE_PARAM, MAX_PAGE_SIZE


class CustomPagination(PageNumberPagination):    
    page_size = PAGE_SIZE
    page_size_query_param = PAGE_SIZE_PARAM
    max_page_size = MAX_PAGE_SIZE 