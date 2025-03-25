from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from http.client import HTTPException
from typing import List

from gridgs.sdk.entity import Session, session_from_dict
from .base_client import BaseClient
from .params import PaginatedQueryParams, SortBy, SortQueryParam


class SessionSortField(Enum):
    START_DATE = 'startDateTime'
    END_DATE = 'endDateTime'
    SATELLITE = 'satellite'
    GROUND_STATION = 'groundStation'
    STATUS = 'status'


@dataclass(frozen=True)
class SessionSortParam(SortBy):
    field: SessionSortField

@dataclass(frozen=True)
class NonPaginatedSessionQueryParams:
    satellite: int | None = None
    ground_station: int | None = None
    status: str | None = None
    date_from: datetime = None
    date_to: datetime = None
    min_tca_elevation: int | None = None

    def to_dict(self) -> dict:
        return {
            'satellite': self.satellite,
            'groundStation': self.ground_station,
            'status': self.status,
            'fromDateTime': self.date_from,
            'toDateTime': self.date_to,
            'minTcaElevation': self.min_tca_elevation
        }


@dataclass(frozen=True)
class SessionQueryParams(PaginatedQueryParams, SortQueryParam, NonPaginatedSessionQueryParams):
    def to_dict(self) -> dict:
        return {
            **PaginatedQueryParams.to_dict(self),
            **SortQueryParam.to_dict(self),
            **NonPaginatedSessionQueryParams.to_dict(self),
        }


@dataclass(frozen=True)
class SessionsResult:
    sessions: List[Session]
    total: int


class SessionClient(BaseClient):

    def find_sessions(self, params: SessionQueryParams) -> SessionsResult:
        response = self.request('get', 'sessions', params=params.to_dict())

        if response.status_code != 200:
            raise HTTPException('Cannot find sessions', response.reason, response.json())

        sessions = []
        for row in response.json():
            sessions.append(session_from_dict(row))

        return SessionsResult(
            sessions=sessions,
            total=int(response.headers.get('Pagination-Count'))
        )

    def predict_sessions(self, params: NonPaginatedSessionQueryParams) -> List[Session]:
        response = self.request('get', 'sessions/predict', params=params.to_dict())

        if response.status_code != 200:
            raise HTTPException('Can not predict session', response.reason, response.json())

        sessions = []
        for row in response.json():
            sessions.append(session_from_dict(row))

        return sessions

    def create_session(self, session: Session) -> Session:
        create_params = {
            'satellite': {'id': session.satellite.id},
            'groundStation': {'id': session.ground_station.id},
            'startDateTime': session.start_datetime.isoformat(sep='T', timespec='auto'),
            'endDateTime': session.end_datetime.isoformat(sep='T', timespec='auto'),
        }

        response = self.request('post', 'sessions', data=create_params)

        if response.status_code != 201:
            raise HTTPException('Can not create session', response.reason, response.json())

        return session_from_dict(response.json())
