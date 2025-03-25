import json
import logging
from http.client import HTTPException
from typing import List

import requests

from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import Session, session_from_dict, Frame, frame_from_dict
from .params import SessionQueryParams, FrameQueryParams


class Client:
    def __init__(self, base_url: str, auth_client: AuthClient, logger: logging.Logger, verify=True):
        self.__base_url = base_url
        self.__auth_client = auth_client
        self.__logger = logger
        self.__verify = verify

    def find_sessions(self, params: SessionQueryParams) -> List[Session]:
        response = requests.get(self.__base_url + '/sessions', params=params.to_dict(), headers=self.__build_auth_header(), verify=self.__verify)

        if response.status_code != 200:
            raise HTTPException('Cannot find sessions', response.reason, response.json())

        sessions = []
        for row in response.json():
            sessions.append(session_from_dict(row))

        return sessions

    def predict_sessions(self, params: SessionQueryParams) -> List[Session]:
        response = requests.get(self.__base_url + '/sessions/predict', params=params.to_dict(), headers=self.__build_auth_header(), verify=self.__verify)

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
        response = requests.post(self.__base_url + '/sessions', data=json.dumps(create_params), headers=self.__build_auth_header(), verify=self.__verify)

        if response.status_code != 201:
            raise HTTPException('Can not create session', response.reason, response.json())

        return session_from_dict(response.json())

    def find_frames(self, params: FrameQueryParams) -> List[Frame]:
        response = requests.get(self.__base_url + '/frames', params=params.to_dict(), headers=self.__build_auth_header(), verify=self.__verify)

        if response.status_code != 200:
            raise HTTPException('Cannot get frames', response.reason, response.json())

        frames = []
        for row in response.json():
            frames.append(frame_from_dict(row))

        return frames

    def __build_auth_header(self) -> dict:
        token = self.__auth_client.token()
        return {'Authorization': 'Bearer ' + token.access_token}