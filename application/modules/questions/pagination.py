from math import ceil

from fastapi import Query


class CustomQuestionPaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=16, ge=1, le=36),
        ordering: str = Query(default="-id"),
        search: str = Query(default=""),
    ):
        self.page = page
        self.per_page = per_page
        self.ordering = ordering
        self.search = search

    @property
    def limit(self):
        return self.per_page

    @property
    def offset(self):
        return (self.page - 1) * self.per_page


class CustomQuestionPaginationResponse:
    def __init__(
        self,
        page: int,
        per_page: int,
        limit: int,
        offset: int,
        base_url,
        route_path: str,
        total_items: int,
    ):
        self.page = page
        self.per_page = per_page
        self.limit = limit
        self.offset = offset
        self.base_url = base_url
        self.route_path = route_path
        self.total_items = total_items

    def the_previous(self):
        if self.offset <= 0:
            return None
        return f"{self.base_url}{self.route_path}/?page={self.page - 1}"

    def the_next(self):
        if self.offset + self.limit >= self.total_items:
            return None
        return f"{self.base_url}{self.route_path}/?page={self.page + 1}"

    def total_pages(self):
        return ceil(self.total_items / self.per_page)
