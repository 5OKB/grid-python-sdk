from dataclasses import dataclass
from enum import Enum
from http.client import HTTPException
from typing import List, Iterator

import requests

from gridgs.sdk.entity import Satellite, satellite_from_dict, Tle, tle_to_dict
from .base_client import BaseClient
from .params import PaginatedQueryParams, SortQueryParam, QueryParams


class SatelliteSortField(Enum):
    NAME = 'name'
    COMPANY = 'company'


@dataclass(frozen=True)
class SatelliteSortQueryParam(SortQueryParam):
    field: SatelliteSortField | None = None


@dataclass(frozen=True)
class NonPaginatedSatelliteQueryParams:
    company: int | None = None

    def to_dict(self) -> dict:
        return {'company': self.company}


@dataclass(frozen=True)
class SatelliteQueryParams(PaginatedQueryParams, SatelliteSortQueryParam, NonPaginatedSatelliteQueryParams):
    def to_dict(self) -> dict:
        return {**PaginatedQueryParams.to_dict(self), **SatelliteSortQueryParam.to_dict(self), **NonPaginatedSatelliteQueryParams.to_dict(self), }


@dataclass(frozen=True)
class SatellitesResult:
    satellites: List[Satellite]
    total: int


class SatelliteClient(BaseClient):
    def find_satellites(self, params: SatelliteQueryParams) -> SatellitesResult:
        response = self.__find_satellites_request(params)

        satellites = []
        for row in response.json():
            satellites.append(satellite_from_dict(row))

        return SatellitesResult(satellites=satellites, total=int(response.headers.get('Pagination-Count')))

    def iterate_satellites(self, params: SatelliteQueryParams) -> Iterator[Satellite]:
        return self._iterate_items(params, self.__find_satellites_request, satellite_from_dict)

    def __find_satellites_request(self, params: QueryParams) -> requests.Response:
        response = self.request('get', 'satellites', params=params.to_dict())

        if response.status_code != 200:
            raise HTTPException('Cannot find satellites', response.reason, response.json())

        return response

    def find_satellite(self, id: int) -> Satellite | None:
        response = self.request('get', f'satellites/{int(id)}')

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise HTTPException('Can not find satellite', response.reason, response.json())

        return satellite_from_dict(response.json())

    def create_satellite(self, satellite: Satellite) -> Satellite:
        create_params = {
            'name': satellite.name,
            'tle': tle_to_dict(satellite.tle),
            'ksy': satellite.ksy,
            'company': {'id': satellite.company.id},
        }

        response = self.request('post', 'satellites', data=create_params)

        if response.status_code != 201:
            raise HTTPException('Can not create satellite', response.reason, response.json())

        return satellite_from_dict(response.json())

    def update_satellite(self, satellite: Satellite) -> Satellite:
        patch_params = {'id': int(satellite.id), }
        if satellite.name != "":
            patch_params['name'] = satellite.name
        if isinstance(satellite.tle, Tle):
            patch_params['tle'] = tle_to_dict(satellite.tle)
        if satellite.ksy != "":
            patch_params['ksy'] = satellite.ksy

        response = self.request('patch', f'satellites/{int(satellite.id)}', data=patch_params)

        if response.status_code != 200:
            raise HTTPException('Can not patch satellite', response.reason, response.json())

        return satellite_from_dict(response.json())
