"""Video stage preprocessing: 16-frame clips of 112x112 frames for C3D."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

CLIP_LENGTH = 16
FRAME_SIZE = 112


def read_frames(video: Path, size: int = FRAME_SIZE, max_frames: int | None = None) -> tuple[np.ndarray, float]:
    """Return (frames as float32 array (n, size, size, 3) in BGR order, fps).

    BGR is kept because the deployed model was trained on frames read with
    OpenCV without a colour conversion.
    """
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise ValueError(f"cannot open video {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frames = []
    while max_frames is None or len(frames) < max_frames:
        ok, img = cap.read()
        if not ok:
            break
        frames.append(cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA))
    cap.release()
    if not frames:
        return np.zeros((0, size, size, 3), np.float32), fps
    return np.asarray(frames, dtype=np.float32), fps


def clips(frames: np.ndarray, length: int = CLIP_LENGTH) -> np.ndarray:
    """Split into non-overlapping clips of ``length`` frames; a short remainder is dropped."""
    n = len(frames) // length
    return frames[: n * length].reshape(n, length, *frames.shape[1:])
