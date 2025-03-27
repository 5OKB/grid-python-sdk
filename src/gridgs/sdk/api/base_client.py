import json
import logging
from urllib.parse import urljoin

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
            urljoin(self.__base_url, path),
            params=params,
            data=json.dumps(data) if isinstance(data, dict) and data else None,
            headers=self.__build_auth_header(),
            verify=self.__verify
        )

    def __build_auth_header(self) -> dict:
        token = self.__auth_client.token()
        return {'Authorization': 'Bearer ' + token.access_token}
