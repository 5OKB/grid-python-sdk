from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from http.client import HTTPException
from typing import List

from gridgs.sdk.entity import frame_from_dict, Frame, FrameType
from .base_client import BaseClient
from .params import PaginatedQueryParams, SortQueryParam


class FrameSortField(Enum):
    CREATED_AT = 'createdAt'
    SESSION = 'communicationSession'
    SATELLITE = 'satellite'
    GROUND_STATION = 'groundStation'
    TYPE = 'type'


@dataclass(frozen=True)
class FrameSortQueryParam(SortQueryParam):
    sort_by: FrameSortField | None = None


@dataclass(frozen=True)
class FrameQueryParams(PaginatedQueryParams, FrameSortQueryParam):
    satellite: int | None = None
    ground_station: int | None = None
    communication_session: int | None = None
    type: FrameType | None = None
    date_from: datetime = None
    date_to: datetime = None

    def to_dict(self) -> dict:
        return {
            **PaginatedQueryParams.to_dict(self),
            **FrameSortQueryParam.to_dict(self),
            'satellite': self.satellite,
            'groundStation': self.ground_station,
            'communicationSession': self.communication_session,
            'type': self.type.value if isinstance(self.type, Enum) else None,
            'fromCreatedAt': self.date_from,
            'toCreatedAt': self.date_to,
        }


@dataclass(frozen=True)
class FramesResult:
    frames: List[Frame]
    total: int


class FrameClient(BaseClient):

    def find_frames(self, params: FrameQueryParams) -> FramesResult:
        response = self.request('get', 'frames', params=params.to_dict())

        if response.status_code != 200:
            raise HTTPException('Cannot get frames', response.reason, response.json())

        frames = []
        for row in response.json():
            frames.append(frame_from_dict(row))

        return FramesResult(frames=frames, total=int(response.headers.get('Pagination-Count')))
