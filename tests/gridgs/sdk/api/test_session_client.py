import logging
import uuid
from datetime import datetime, timedelta, timezone
from os import environ as env

from keycloak import KeycloakOpenID

from gridgs.sdk.api import Client as ApiClient, SessionQueryParams, NonPaginatedSessionQueryParams, SessionsResult
from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import Session, Satellite, GroundStation, HorizontalCoords


class TestSessionClient:
    auth_client: AuthClient
    api_client: ApiClient

    @classmethod
    def setup_class(cls):
        keycloak_openid = KeycloakOpenID(server_url=env.get('GRID_OAUTH_URL'), client_id=env.get('GRID_OAUTH_CLIENT_ID'), realm_name=env.get('GRID_OAUTH_REALM'))
        cls.auth_client = AuthClient(open_id_client=keycloak_openid, username=env.get('GRID_OAUTH_USERNAME'), password=env.get('GRID_OAUTH_PASSWORD'), company_id=int(env.get('GRID_OAUTH_COMPANY_ID')),
                                     logger=logging.getLogger('auth_client'))
        cls.api_client = ApiClient(base_url=env.get('GRID_API_URL'), auth_client=cls.auth_client, logger=logging.getLogger('api_client'))

    def teardown_class(self):
        self.auth_client.logout()

    def test_find_success(self):
        expected_count = 3

        query_params = SessionQueryParams(limit=expected_count)

        result = self.api_client.find_sessions(query_params)

        assert isinstance(result, SessionsResult)
        assert result.total >= expected_count
        assert expected_count == len(result.sessions)

        for session in result.sessions:
            assert_session_fields_valid(session)

    def test_find_by_id_success(self):
        result = self.api_client.find_sessions(SessionQueryParams(limit=1))
        assert len(result.sessions) == 1

        first_session = result.sessions[0]
        assert_session_fields_valid(first_session)

        found_session = self.api_client.find_session(first_session.id)
        assert_session_fields_valid(found_session)

        assert found_session.id == first_session.id
        assert found_session.satellite.id == first_session.satellite.id

    def test_not_found_by_id_success(self):
        not_existing_id = uuid.UUID('12345678-5555-5555-5555-555555555432')

        found_session = self.api_client.find_session(not_existing_id)
        assert found_session is None

    def test_predict_and_create_and_delete_success(self):
        expected_from = datetime.now(timezone.utc) + timedelta(days=14)
        expected_to = expected_from + timedelta(days=7)
        expected_min_tca_elevation = 10

        # Predicting sessions
        query_params = NonPaginatedSessionQueryParams(date_from=expected_from, date_to=expected_to, min_tca_elevation=expected_min_tca_elevation)

        sessions = self.api_client.predict_sessions(query_params)

        assert isinstance(sessions, list)
        assert len(sessions) > 0, 'Can not predict sessions. Check free slots on GRID side'

        for session in sessions:
            assert_session_fields_valid(session)
            assert session.start_datetime <= expected_to
            assert session.end_datetime >= expected_from
            assert session.tca_coords.elevation >= expected_min_tca_elevation

        # Creating a session
        predicted_session = sessions[0]

        created_session = self.api_client.create_session(predicted_session)

        assert_session_fields_valid(created_session)
        assert predicted_session.id == created_session.id

        assert predicted_session.satellite.id == created_session.satellite.id
        assert predicted_session.ground_station.id == created_session.ground_station.id
        assert predicted_session.start_datetime <= created_session.start_datetime
        assert predicted_session.end_datetime >= created_session.end_datetime

        double_checked_session = self.api_client.find_session(created_session.id)
        assert isinstance(double_checked_session, Session)
        assert double_checked_session.id == created_session.id

        # Deleting the session
        self.api_client.delete_session(created_session.id)

        should_be_none = self.api_client.find_session(created_session.id)
        assert should_be_none is None


def assert_session_fields_valid(session: Session) -> None:
    assert isinstance(session, Session)
    assert isinstance(session.id, uuid.UUID)
    assert isinstance(session.satellite, Satellite)
    assert session.satellite.id > 0
    assert isinstance(session.ground_station, GroundStation)
    assert session.ground_station.id > 0
    assert isinstance(session.start_datetime, datetime)
    assert isinstance(session.end_datetime, datetime)
    assert isinstance(session.tca_coords, HorizontalCoords)
