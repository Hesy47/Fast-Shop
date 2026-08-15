from math import ceil
from urllib.parse import urlencode

from fastapi import Query


class CustomScrollPaginationParams:
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


class CustomScrollPaginationResponse:
    def __init__(
        self,
        page: int,
        per_page: int,
        limit: int,
        offset: int,
        base_url,
        route_path: str,
        total_items: int,
        query_params=None,
    ):
        self.page = page
        self.per_page = per_page
        self.limit = limit
        self.offset = offset
        self.base_url = base_url
        self.route_path = route_path
        self.total_items = total_items
        self.query_params = query_params

    def _page_url(self, page: int):
        query_items = (
            [
                (key, value)
                for key, value in self.query_params.multi_items()
                if key == "per_page"
            ]
            if self.query_params is not None
            else []
        )
        query_items.append(("page", page))
        return f"{self.base_url}{self.route_path}/?{urlencode(query_items)}"

    def the_previous(self):
        return self._page_url(self.page - 1) if self.offset > 0 else None

    def the_next(self):
        has_next = self.offset + self.limit < self.total_items
        return self._page_url(self.page + 1) if has_next else None

    def total_pages(self):
        return ceil(self.total_items / self.per_page)
