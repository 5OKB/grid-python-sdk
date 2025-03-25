from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class PaginatedQueryParams:
    limit: int | None = None
    offset: int | None = None

    def to_dict(self) -> dict:
        return {'offset': self.offset, 'limit': self.limit}


class SortOrder(Enum):
    ASC = 'asc'
    DESC = 'desc'


@dataclass(frozen=True)
class SortBy:
    field: Enum
    order: SortOrder


@dataclass(frozen=True)
class SortQueryParam:
    sort_by: SortBy | None = None

    def to_dict(self) -> dict:
        return {
            'sort_by': f'{self.sort_by.field.value}.{self.sort_by.order.value}' if isinstance(self.sort_by, SortBy) else None
        }
