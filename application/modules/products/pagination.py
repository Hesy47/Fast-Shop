from math import ceil

from fastapi import Query


class CustomProductPaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=16, le=36),
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


class CustomProductPaginationResponse:
    def __init__(
        self, page, per_page, limit, offset, base_url, route_path, total_items
    ):
        self.page = page
        self.per_page = per_page
        self.limit = limit
        self.offset = offset
        self.base_url = base_url
        self.route_path = route_path
        self.total_items = total_items

    def the_previous(self):
        has_previous = self.offset > 0
        return (
            f"{self.base_url}{self.route_path}/?page={self.page-1}"
            if has_previous
            else None
        )

    def the_next(self):
        has_next = self.offset + self.limit < self.total_items
        return (
            f"{self.base_url}{self.route_path}/?page={self.page+1}"
            if has_next
            else None
        )

    def total_pages(self):
        return ceil(self.total_items / self.per_page)


class CustomProductImagePaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=16, le=36),
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


class CustomProductImagePaginationResponse:
    def __init__(
        self, page, per_page, limit, offset, base_url, route_path, total_items
    ):
        self.page = page
        self.per_page = per_page
        self.limit = limit
        self.offset = offset
        self.base_url = base_url
        self.route_path = route_path
        self.total_items = total_items

    def the_previous(self):
        has_previous = self.offset > 0
        return (
            f"{self.base_url}{self.route_path}/?page={self.page-1}"
            if has_previous
            else None
        )

    def the_next(self):
        has_next = self.offset + self.limit < self.total_items
        return (
            f"{self.base_url}{self.route_path}/?page={self.page+1}"
            if has_next
            else None
        )

    def total_pages(self):
        return ceil(self.total_items / self.per_page)


class CustomProductInformationPaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=16, le=36),
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


class CustomProductInformationPaginationResponse:
    def __init__(
        self, page, per_page, limit, offset, base_url, route_path, total_items
    ):
        self.page = page
        self.per_page = per_page
        self.limit = limit
        self.offset = offset
        self.base_url = base_url
        self.route_path = route_path
        self.total_items = total_items

    def the_previous(self):
        has_previous = self.offset > 0
        return (
            f"{self.base_url}{self.route_path}/?page={self.page-1}"
            if has_previous
            else None
        )

    def the_next(self):
        has_next = self.offset + self.limit < self.total_items
        return (
            f"{self.base_url}{self.route_path}/?page={self.page+1}"
            if has_next
            else None
        )

    def total_pages(self):
        return ceil(self.total_items / self.per_page)
