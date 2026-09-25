import numpy as np
import pytest

from violence_detection import audio


def test_spectrogram_shape_and_bins():
    rate = audio.SAMPLE_RATE
    t = np.arange(rate) / rate
    spec = audio.spectrogram(np.sin(2 * np.pi * 1000 * t))
    assert spec.shape == (1 + (rate - 255) // 128, 129)
    # 1 kHz tone -> peak at bin 1000 / (44000 / 256) ~= 5.8
    assert abs(int(spec.mean(0).argmax()) - 6) <= 1


def test_spectrogram_matches_tensorflow_when_available():
    tf = pytest.importorskip("tensorflow")
    x = np.random.default_rng(0).standard_normal(5000).astype(np.float32)
    ref = np.abs(tf.signal.stft(x, frame_length=255, frame_step=128).numpy())
    np.testing.assert_allclose(audio.spectrogram(x), ref, rtol=1e-4, atol=1e-4)


def test_short_waveform_gives_empty_spectrogram():
    assert audio.spectrogram(np.zeros(100)).shape == (0, 129)


def test_fit_frames_pads_and_truncates():
    spec = np.ones((10, 129), np.float32)
    padded = audio.fit_frames(spec, 16)
    assert padded.shape == (16, 129) and padded[:10].all() and not padded[10:].any()
    long = np.arange(20 * 129, dtype=np.float32).reshape(20, 129)
    np.testing.assert_array_equal(audio.fit_frames(long, 16), long[:16])


def test_resample_changes_length():
    x = np.zeros(48_000, np.float32)
    assert len(audio.resample(x, 48_000)) == audio.SAMPLE_RATE
    assert audio.resample(x, audio.SAMPLE_RATE) is x


def test_features_from_real_video(video_with_audio):
    f = audio.features(video_with_audio)
    assert f.shape == (1, audio.TIME_FRAMES, 129)
    assert f[0, :100].max() > 0                    # 2 s of tone fills the first ~690 frames
    assert not f[0, 800:].any()                    # and the rest is padding


def test_silent_video_raises_no_audio(silent_video, tmp_path):
    pytest.importorskip("shutil").which("ffmpeg") or pytest.skip("ffmpeg not installed")
    with pytest.raises(audio.NoAudio):
        audio.extract_wav(silent_video, tmp_path)
