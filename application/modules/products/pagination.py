from math import ceil
from urllib.parse import urlencode

from fastapi import Query


class PublicProductPaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=16, le=36),
        ordering: str = Query(default="-id"),
        search: str = Query(default=""),
        collection_id: int | None = Query(default=None, ge=1),
        sub_collection_id: int | None = Query(default=None, ge=1),
        has_discount: bool | None = Query(default=None),
        min_price: int = Query(default=0, ge=0),
        max_price: int = Query(default=100_000_000, ge=0),
    ):
        self.page = page
        self.per_page = per_page
        self.ordering = ordering
        self.search = search
        self.collection_id = collection_id
        self.sub_collection_id = sub_collection_id
        self.has_discount = has_discount
        self.min_price = min_price
        self.max_price = max_price

    @property
    def limit(self):
        return self.per_page

    @property
    def offset(self):
        return (self.page - 1) * self.per_page


class PublicProductPaginationResponse:
    def __init__(
        self,
        page,
        per_page,
        limit,
        offset,
        base_url,
        route_path,
        total_items,
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
                if key != "page"
            ]
            if self.query_params is not None
            else []
        )
        query_items.append(("page", page))
        return f"{self.base_url}{self.route_path}/?{urlencode(query_items)}"

    def the_previous(self):
        has_previous = self.offset > 0
        return self._page_url(self.page - 1) if has_previous else None

    def the_next(self):
        has_next = self.offset + self.limit < self.total_items
        return self._page_url(self.page + 1) if has_next else None

    def total_pages(self):
        return ceil(self.total_items / self.per_page)


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
