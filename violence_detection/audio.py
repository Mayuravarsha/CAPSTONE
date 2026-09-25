"""Audio stage preprocessing: extract the soundtrack and turn it into a spectrogram.

The spectrogram matches the TensorFlow code used in training,
``abs(tf.signal.stft(waveform, frame_length=255, frame_step=128))``, but is
computed with NumPy so the preprocessing can be tested without TensorFlow.
tf.signal.stft uses tf.signal.hann_window(periodic=True), which only differs
from the symmetric window for even lengths (for 255 samples the denominator is
254), and an FFT length of the next power of two (256): 129 frequency bins.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly

SAMPLE_RATE = 44_000          # the rate used when the audio model was trained
FRAME_LENGTH = 255
FRAME_STEP = 128
FFT_LENGTH = 256
TIME_FRAMES = 1024            # spectrogram rows fed to the model (padded or cut)


class NoAudio(Exception):
    """The video has no audio track, or ffmpeg is unavailable."""


def extract_wav(video: Path, out_dir: Path) -> Path:
    """Decode the audio track to a mono 16-bit WAV at SAMPLE_RATE using ffmpeg."""
    if shutil.which("ffmpeg") is None:
        raise NoAudio("ffmpeg is not installed")
    wav = out_dir / (video.stem + ".wav")
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1",
         "-ar", str(SAMPLE_RATE), "-acodec", "pcm_s16le", str(wav)],
        capture_output=True, timeout=120)
    if proc.returncode != 0 or not wav.exists() or wav.stat().st_size <= 44:
        raise NoAudio(proc.stderr.decode(errors="replace").strip() or "no audio stream")
    return wav


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    """Read a 16-bit PCM WAV as float32 in [-1, 1], mixed down to mono."""
    with wave.open(str(path)) as w:
        rate, channels, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if width != 2:
        raise ValueError("expected 16-bit PCM audio")
    data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    return data.reshape(-1, channels).mean(axis=1), rate


def resample(waveform: np.ndarray, rate: int, target: int = SAMPLE_RATE) -> np.ndarray:
    if rate == target:
        return waveform
    g = np.gcd(rate, target)
    return resample_poly(waveform, target // g, rate // g).astype(np.float32)


def spectrogram(waveform: np.ndarray) -> np.ndarray:
    """|STFT| with shape (frames, 129), identical to tf.signal.stft defaults."""
    waveform = np.asarray(waveform, dtype=np.float32)
    if len(waveform) < FRAME_LENGTH:
        return np.zeros((0, FFT_LENGTH // 2 + 1), np.float32)
    n = 1 + (len(waveform) - FRAME_LENGTH) // FRAME_STEP
    idx = np.arange(FRAME_LENGTH)[None, :] + FRAME_STEP * np.arange(n)[:, None]
    denom = FRAME_LENGTH - (FRAME_LENGTH % 2)          # tf: length + periodic*even - 1
    window = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(FRAME_LENGTH) / denom)
    return np.abs(np.fft.rfft(waveform[idx] * window, n=FFT_LENGTH)).astype(np.float32)


def fit_frames(spec: np.ndarray, frames: int = TIME_FRAMES) -> np.ndarray:
    """Cut or zero-pad the time axis to ``frames`` rows (what ndarray.resize did originally)."""
    out = np.zeros((frames, spec.shape[1]), np.float32)
    out[: min(frames, len(spec))] = spec[:frames]
    return out


def features(video: Path) -> np.ndarray:
    """Video file -> model input of shape (1, TIME_FRAMES, 129)."""
    with tempfile.TemporaryDirectory() as tmp:
        wav = extract_wav(Path(video), Path(tmp))
        waveform, rate = read_wav(wav)
    return fit_frames(spectrogram(resample(waveform, rate)))[None]
