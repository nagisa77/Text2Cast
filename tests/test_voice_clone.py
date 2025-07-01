import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest import mock
import tempfile
from text2cast.voice_clone import clone_voice
import os

os.environ.setdefault('VOLCENGINE_TOKEN', 'token')
os.environ.setdefault('VOLCENGINE_APP_ID', 'appid')


@mock.patch('requests.post')
def test_clone_voice(mock_post):
    tmp = tempfile.TemporaryDirectory()
    f1 = Path(tmp.name) / '1.wav'
    f1.write_bytes(b'data1')
    f2 = Path(tmp.name) / '2.wav'
    f2.write_bytes(b'data2')

    class Dummy:
        def raise_for_status(self):
            pass
        def json(self):
            return {"data": {"voice_id": "vid"}}

    mock_post.return_value = Dummy()
    voice_id = clone_voice([str(f1), str(f2)], 'test_voice')
    assert voice_id == 'vid'
    tmp.cleanup()
