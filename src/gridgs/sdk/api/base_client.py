import logging

import requests

from gridgs.sdk.auth import Client as AuthClient


class BaseClient:
    def __init__(self, base_url: str, auth_client: AuthClient, logger: logging.Logger, verify=True):
        self.__base_url = base_url
        self.__auth_client = auth_client
        self.__logger = logger
        self.__verify = verify

    def request(self, method: str, path: str, params: dict | None = None, data: dict | None = None) -> requests.Response:
        return requests.request(
            method,
            self.__base_url + '/' + path,
            params=params,
            data=data,
            headers=self.__build_auth_header(),
            verify=self.__verify
        )

    def __build_auth_header(self) -> dict:
        token = self.__auth_client.token()
        return {'Authorization': 'Bearer ' + token.access_token}
