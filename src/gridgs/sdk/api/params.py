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
class SortQueryParam:
    sort_by: Enum | None = None
    sort_order: SortOrder = SortOrder.ASC

    def to_dict(self) -> dict:
        return {'sort_by': f'{self.sort_by.value}.{self.sort_order.value}' if isinstance(self.sort_by, Enum) else None}
