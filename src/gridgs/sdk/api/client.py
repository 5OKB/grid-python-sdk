from .frame_client import FrameClient
from .satellite_client import SatelliteClient
from .session_client import SessionClient


class Client(FrameClient, SatelliteClient, SessionClient):
    pass
