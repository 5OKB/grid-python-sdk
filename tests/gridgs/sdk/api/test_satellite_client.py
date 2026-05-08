import logging
from os import environ as env

from keycloak import KeycloakOpenID

from gridgs.sdk.api import Client as ApiClient, SatelliteQueryParams, SatellitesResult
from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import Company, Satellite, Tle


class TestSatelliteClient:
    auth_client: AuthClient
    api_client: ApiClient

    @classmethod
    def setup_class(cls):
        keycloak_openid = KeycloakOpenID(server_url=env.get('GRID_OAUTH_URL'), client_id=env.get('GRID_OAUTH_CLIENT_ID'), realm_name=env.get('GRID_OAUTH_REALM'))
        cls.auth_client = AuthClient(open_id_client=keycloak_openid, username=env.get('GRID_OAUTH_USERNAME'), password=env.get('GRID_OAUTH_PASSWORD'), logger=logging.getLogger('auth_client'))
        cls.api_client = ApiClient(base_url=env.get('GRID_API_URL'), auth_client=cls.auth_client, logger=logging.getLogger('api_client'))

    def teardown_class(self):
        self.auth_client.logout()

    def test_find_success(self):
        expected_count = 2

        query_params = SatelliteQueryParams(limit=expected_count)

        result = self.api_client.find_satellites(query_params)

        assert isinstance(result, SatellitesResult)
        assert result.total >= expected_count
        assert expected_count == len(result.satellites)

        for satellite in result.satellites:
            assert_satellite_fields_valid(satellite)

    def test_find_by_id_success(self):
        result = self.api_client.find_satellites(SatelliteQueryParams(limit=1))
        assert len(result.satellites) == 1

        first_satellite = result.satellites[0]
        assert_satellite_fields_valid(first_satellite)

        found_satellite = self.api_client.find_satellite(first_satellite.id)
        assert_satellite_fields_valid(found_satellite)

        assert found_satellite.id == first_satellite.id
        assert found_satellite.company.id == first_satellite.company.id

    def test_not_found_by_id_success(self):
        not_existing_id = 9999999999

        found_satellite = self.api_client.find_satellite(not_existing_id)
        assert found_satellite is None


def assert_satellite_fields_valid(satellite: Satellite) -> None:
    assert isinstance(satellite, Satellite)
    assert isinstance(satellite.id, int)
    assert satellite.id > 0
    assert isinstance(satellite.company, Company)
    assert satellite.company.id > 0
    assert isinstance(satellite.name, str)
    assert satellite.name
    assert isinstance(satellite.tle, Tle)
