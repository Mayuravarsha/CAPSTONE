"""The two-stage decision.

1. The audio model scores the soundtrack. If it is confident the audio is
   violent (probability above ``audio_threshold``), the video is flagged and
   the expensive video model is skipped.
2. Otherwise every 16-frame clip is scored by the video model. A clip counts
   as violent above ``clip_threshold``, and the video is violent when the
   share of violent clips exceeds ``video_threshold``.

The thresholds are those of the deployed system (0.8, 0.75 and 0.7). Models
are passed in as plain callables, so the logic can be tested with stubs and
the TensorFlow models are only loaded by the server.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from . import audio as audio_mod
from . import video as video_mod

AudioModel = Callable[[np.ndarray], float]           # (1, frames, 129) -> P(violent)
VideoModel = Callable[[np.ndarray], np.ndarray]      # (n, 16, 112, 112, 3) -> P(violent) per clip


@dataclass
class Clip:
    start: float
    end: float
    probability: float


@dataclass
class Result:
    violent: bool
    decided_by: str                       # "audio", "video" or "none"
    audio_probability: float | None
    violent_clip_share: float | None
    clips: list[Clip] = field(default_factory=list)
    seconds: float = 0.0
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class Cascade:
    def __init__(self, audio_model: AudioModel | None, video_model: VideoModel,
                 audio_threshold: float = 0.8, clip_threshold: float = 0.75,
                 video_threshold: float = 0.7, batch_size: int = 8):
        self.audio_model = audio_model
        self.video_model = video_model
        self.audio_threshold = audio_threshold
        self.clip_threshold = clip_threshold
        self.video_threshold = video_threshold
        self.batch_size = batch_size

    def score_audio(self, video: Path) -> float | None:
        if self.audio_model is None:
            return None
        try:
            return float(self.audio_model(audio_mod.features(video)))
        except audio_mod.NoAudio:
            return None

    def score_clips(self, frames: np.ndarray) -> np.ndarray:
        batches = video_mod.clips(frames)
        probs = [np.ravel(self.video_model(batches[i:i + self.batch_size]))
                 for i in range(0, len(batches), self.batch_size)]
        return np.concatenate(probs) if probs else np.zeros(0)

    def analyse(self, video: Path) -> Result:
        start = time.perf_counter()
        audio_p = self.score_audio(Path(video))
        if audio_p is not None and audio_p > self.audio_threshold:
            return Result(True, "audio", audio_p, None, seconds=time.perf_counter() - start)

        frames, fps = video_mod.read_frames(Path(video))
        probs = self.score_clips(frames)
        if len(probs) == 0:
            return Result(False, "none", audio_p, None, seconds=time.perf_counter() - start,
                          note=f"video shorter than {video_mod.CLIP_LENGTH} frames")
        L = video_mod.CLIP_LENGTH
        timeline = [Clip(round(i * L / fps, 2), round((i + 1) * L / fps, 2), float(p))
                    for i, p in enumerate(probs)]
        share = float(np.mean(probs >= self.clip_threshold))
        return Result(share > self.video_threshold, "video", audio_p, share, timeline,
                      seconds=time.perf_counter() - start)
