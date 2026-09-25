import numpy as np
import pytest

from violence_detection import audio, video
from violence_detection.cascade import Cascade

from .conftest import write_video


class VideoStub:
    """Returns fixed per-clip probabilities and records how it was called."""

    def __init__(self, probs):
        self.probs, self.calls, self.seen = list(probs), 0, 0

    def __call__(self, clips):
        assert clips.shape[1:] == (16, 112, 112, 3)
        out = self.probs[self.seen:self.seen + len(clips)]
        self.calls += 1
        self.seen += len(clips)
        return np.array(out)


def test_clips_drop_the_remainder():
    frames = np.zeros((50, 112, 112, 3), np.float32)
    assert video.clips(frames).shape == (3, 16, 112, 112, 3)
    assert video.clips(frames[:15]).shape[0] == 0


def test_read_frames(silent_video):
    frames, fps = video.read_frames(silent_video)
    assert frames.shape == (50, 112, 112, 3) and fps == pytest.approx(25)
    assert frames[..., 2].mean() > 200            # red stays in channel 2 (BGR)


def test_violent_when_enough_clips_are_violent(silent_video):
    stub = VideoStub([0.9, 0.8, 0.95])
    r = Cascade(None, stub).analyse(silent_video)
    assert r.violent and r.decided_by == "video"
    assert r.violent_clip_share == 1.0
    assert [c.start for c in r.clips] == [0.0, 0.64, 1.28]


def test_share_must_exceed_video_threshold(silent_video):
    r = Cascade(None, VideoStub([0.9, 0.9, 0.1])).analyse(silent_video)   # 2/3 < 0.7
    assert not r.violent and r.violent_clip_share == pytest.approx(2 / 3)


def test_clip_threshold_is_inclusive(silent_video):
    r = Cascade(None, VideoStub([0.75, 0.75, 0.75])).analyse(silent_video)
    assert r.violent


def test_batches(tmp_path):
    path = write_video(tmp_path / "long.avi", frames=16 * 10)
    stub = VideoStub([0.1] * 10)
    Cascade(None, stub, batch_size=4).analyse(path)
    assert stub.calls == 3 and stub.seen == 10


def test_confident_audio_skips_video(silent_video, monkeypatch):
    monkeypatch.setattr(audio, "features", lambda _v: np.zeros((1, 1024, 129)))
    stub = VideoStub([])
    r = Cascade(lambda spec: 0.93, stub).analyse(silent_video)
    assert r.violent and r.decided_by == "audio" and stub.calls == 0


def test_unsure_audio_falls_through_to_video(silent_video, monkeypatch):
    monkeypatch.setattr(audio, "features", lambda _v: np.zeros((1, 1024, 129)))
    r = Cascade(lambda spec: 0.6, VideoStub([0.1, 0.2, 0.1])).analyse(silent_video)
    assert not r.violent and r.decided_by == "video" and r.audio_probability == 0.6


def test_missing_audio_track_is_not_an_error(silent_video, monkeypatch):
    def no_audio(_v):
        raise audio.NoAudio("no audio stream")
    monkeypatch.setattr(audio, "features", no_audio)
    r = Cascade(lambda s: 1.0, VideoStub([0.1] * 3)).analyse(silent_video)
    assert r.audio_probability is None and r.decided_by == "video"


def test_too_short_video(tmp_path):
    r = Cascade(None, VideoStub([])).analyse(write_video(tmp_path / "short.avi", frames=10))
    assert not r.violent and r.decided_by == "none" and "shorter" in r.note


def test_unreadable_file(tmp_path):
    bad = tmp_path / "bad.mp4"
    bad.write_bytes(b"not a video")
    with pytest.raises(ValueError):
        Cascade(None, VideoStub([])).analyse(bad)
