import logging
import uuid
from datetime import datetime, timezone, timedelta
from os import environ as env
from threading import Thread
from time import sleep
from typing import List

from keycloak import KeycloakOpenID

from gridgs.sdk.api import Client as ApiClient, NonPaginatedSessionQueryParams
from gridgs.sdk.auth import Client as AuthClient
from gridgs.sdk.entity import Session, SessionEvent
from gridgs.sdk.event import Subscriber as GridEventSubscriber


class EventsCollector:
    def __init__(self):
        self.rows: List[SessionEvent] = []


class TestSubscriber:
    auth_client: AuthClient
    api_client: ApiClient
    event_subscriber: GridEventSubscriber
    th_event_subscriber: Thread
    events_collector: EventsCollector

    @classmethod
    def setup_class(cls):
        # DI
        keycloak_openid = KeycloakOpenID(server_url=env.get('GRID_OAUTH_URL'), client_id=env.get('GRID_OAUTH_CLIENT_ID'), realm_name=env.get('GRID_OAUTH_REALM'))
        cls.auth_client = AuthClient(open_id_client=keycloak_openid, username=env.get('GRID_OAUTH_USERNAME'), password=env.get('GRID_OAUTH_PASSWORD'), company_id=int(env.get('GRID_OAUTH_COMPANY_ID')),
                                     logger=logging.getLogger('auth_client'))
        cls.api_client = ApiClient(base_url=env.get('GRID_API_URL'), auth_client=cls.auth_client, logger=logging.getLogger('api_client'))
        cls.event_subscriber = GridEventSubscriber(host=env.get('GRID_MQTT_HOST'), port=int(env.get('GRID_MQTT_PORT')), auth_client=cls.auth_client, logger=logging.getLogger('event_subscriber'))
        cls.events_collector = EventsCollector()

        # DI done

        # Setup and run subscriber
        def _on_event(event: SessionEvent):
            assert isinstance(event, SessionEvent)
            assert isinstance(event.session, Session)
            assert isinstance(event.session.id, uuid.UUID)

            if event.session.created_by == env.get('GRID_OAUTH_USERNAME'):
                cls.events_collector.rows.append(event)

        cls.event_subscriber.on_event(_on_event)
        cls.th_event_subscriber = Thread(target=cls.event_subscriber.run)
        cls.th_event_subscriber.start()
        sleep(1)

    def teardown_class(self):
        self.event_subscriber.stop()
        self.th_event_subscriber.join()
        self.auth_client.logout()

    def setup_method(self, method):
        self.events_collector.rows = []

    def test_new_session_event_success(self):
        assert len(self.events_collector.rows) == 0

        # Create session (should trigger the event)
        created_session = predict_and_create_session(self.api_client)

        # Delete (should trigger the event)
        self.api_client.delete_session(created_session.id)

        sleep(1)

        assert len(self.events_collector.rows) == 2

        create_event = self.events_collector.rows[0]
        assert create_event.type == SessionEvent.EVENT_CREATE
        assert create_event.session.id == created_session.id

        remove_event = self.events_collector.rows[1]
        assert remove_event.type == SessionEvent.EVENT_REMOVE
        assert remove_event.session.id == created_session.id


def predict_and_create_session(api_client: ApiClient) -> Session:
    predicted_sessions = api_client.predict_sessions(NonPaginatedSessionQueryParams(date_from=datetime.now(timezone.utc) + timedelta(days=14)))
    assert len(predicted_sessions) > 0, 'Can not predict sessions. Check free slots on GRID-GS side'

    # Create (should trigger the event)
    first_predicted_session = predicted_sessions[0]
    assert isinstance(first_predicted_session, Session)

    created_session = api_client.create_session(first_predicted_session)
    assert isinstance(created_session, Session)

    return created_session
