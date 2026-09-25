import io

from violence_detection.api import create_app
from violence_detection.cascade import Cascade

from .test_cascade import VideoStub


def client(probs=(0.9, 0.9, 0.9), max_mb=None, monkeypatch=None):
    if max_mb is not None:
        monkeypatch.setenv("VD_MAX_MB", str(max_mb))
    app = create_app(Cascade(None, VideoStub(probs)))
    app.testing = True
    return app.test_client()


def test_health():
    r = client().get("/api/health")
    assert r.json == {"status": "ok", "models_loaded": True}


def test_analyze_returns_result(silent_video):
    with open(silent_video, "rb") as f:
        r = client().post("/api/analyze", data={"file": (f, "fight.avi")},
                          content_type="multipart/form-data")
    assert r.status_code == 200
    assert r.json["violent"] is True and len(r.json["clips"]) == 3
    assert r.headers["Access-Control-Allow-Origin"]


def test_missing_file():
    r = client().post("/api/analyze", data={}, content_type="multipart/form-data")
    assert r.status_code == 400


def test_rejects_non_video_extension():
    r = client().post("/api/analyze", data={"file": (io.BytesIO(b"x"), "notes.exe")},
                      content_type="multipart/form-data")
    assert r.status_code == 415


def test_rejects_unreadable_video():
    r = client().post("/api/analyze", data={"file": (io.BytesIO(b"garbage"), "clip.mp4")},
                      content_type="multipart/form-data")
    assert r.status_code == 422


def test_upload_limit(monkeypatch):
    c = client(max_mb=1, monkeypatch=monkeypatch)
    big = io.BytesIO(b"0" * (2 * 1024 * 1024))
    r = c.post("/api/analyze", data={"file": (big, "big.mp4")}, content_type="multipart/form-data")
    assert r.status_code == 413


def test_path_traversal_name_is_sanitised(silent_video):
    with open(silent_video, "rb") as f:
        r = client().post("/api/analyze", data={"file": (f, "../../etc/evil.avi")},
                          content_type="multipart/form-data")
    assert r.status_code == 200
