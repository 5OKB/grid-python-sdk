import logging
import uuid
from datetime import datetime
from os import environ as env

from keycloak import KeycloakOpenID

from gridgs.sdk.api import Client as ApiClient, FrameQueryParams, FramesResult
from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import Session, Frame, Satellite, GroundStation


class TestFrameClient:
    auth_client: AuthClient
    api_client: ApiClient

    @classmethod
    def setup_class(cls):
        # DI
        keycloak_openid = KeycloakOpenID(server_url=env.get('GRID_OAUTH_URL'), client_id=env.get('GRID_OAUTH_CLIENT_ID'), realm_name=env.get('GRID_OAUTH_REALM'))
        cls.auth_client = AuthClient(open_id_client=keycloak_openid, username=env.get('GRID_OAUTH_USERNAME'), password=env.get('GRID_OAUTH_PASSWORD'), company_id=int(env.get('GRID_OAUTH_COMPANY_ID')),
                                     logger=logging.getLogger('auth_client'))
        cls.api_client = ApiClient(base_url=env.get('GRID_API_URL'), auth_client=cls.auth_client, logger=logging.getLogger('api_client'))

    def teardown_class(self):
        self.auth_client.logout()

    def test_find_success(self):
        expected_count = 3

        query_params = FrameQueryParams(limit=expected_count)

        result = self.api_client.find_frames(query_params)

        assert isinstance(result, FramesResult)
        assert result.total >= expected_count
        assert expected_count == len(result.frames)

        for frame in result.frames:
            assert_frame_fields_valid(frame)


def assert_frame_fields_valid(frame: Frame) -> None:
    assert isinstance(frame, Frame)
    assert isinstance(frame.id, uuid.UUID)

    assert isinstance(frame.session, Session)
    assert isinstance(frame.session.id, uuid.UUID)

    assert isinstance(frame.satellite, Satellite)
    assert frame.satellite.id > 0

    assert isinstance(frame.ground_station, GroundStation)
    assert frame.ground_station.id > 0

    assert isinstance(frame.created_at, datetime)

    assert isinstance(frame.raw_data, bytes)
