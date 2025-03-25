import base64
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .ground_station import GroundStation, ground_station_from_dict
from .satellite import Satellite, satellite_from_dict
from .session import Session, session_from_dict

class FrameType(Enum):
    RECEIVED = 1
    SENT = 2


@dataclass(frozen=True)
class Frame:
    id: uuid.UUID
    created_at: datetime
    type: FrameType
    satellite: Satellite
    ground_station: GroundStation
    session: Session
    raw_data: bytes
    extra_data: dict = None


def frame_from_dict(fr: dict) -> Frame:
    return Frame(
        id=uuid.UUID(fr['id']),
        created_at=datetime.fromisoformat(fr['createdAt']) if 'createdAt' in fr else None,
        type=FrameType(fr['type']) if 'type' in fr else None,
        satellite=satellite_from_dict(fr['satellite']) if 'satellite' in fr else None,
        ground_station=ground_station_from_dict(fr['groundStation']) if 'groundStation' in fr else None,
        session=session_from_dict(fr['communicationSession']) if 'communicationSession' in fr else None,
        raw_data=base64.b64decode(fr['rawData']) if 'rawData' in fr else None,
        extra_data=fr['extraData'] if 'extraData' in fr else None)
