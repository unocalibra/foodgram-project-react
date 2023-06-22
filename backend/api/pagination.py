from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    """
    Создание своего пагинатора.
    """
    page_size = 6
    page_size_query_param = 'limit'
