import uuid

from gridgs.sdk.entity import frame_from_dict


def test_can_be_created_from_dict():
    expected_id = '00000001-0001-0001-0001-000000000001'

    frame = frame_from_dict({'id': expected_id})

    assert isinstance(frame.id, uuid.UUID)
    assert expected_id == str(frame.id)
