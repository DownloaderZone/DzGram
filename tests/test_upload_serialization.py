import pytest

from pyrogram import raw
from pyrogram.session.session import _serialize_file_part


@pytest.mark.parametrize("size", [0, 1, 252, 253, 254, 255, 512 * 1024])
@pytest.mark.parametrize("big", [False, True])
def test_upload_fast_serialization_matches_wire_format(size, big):
    args = dict(file_id=123, file_part=2, bytes=b"x" * size)
    if big:
        query = raw.functions.upload.SaveBigFilePart(file_total_parts=10, **args)
    else:
        query = raw.functions.upload.SaveFilePart(**args)
    assert _serialize_file_part(query) == query.write()


def test_non_upload_uses_normal_serializer():
    assert _serialize_file_part(raw.functions.Ping(ping_id=0)) is None
