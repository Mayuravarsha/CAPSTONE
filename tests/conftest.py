import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
import pytest


def write_video(path: Path, frames: int, fps: int = 25, colour=(0, 0, 255)) -> Path:
    w = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (160, 120))
    for i in range(frames):
        img = np.full((120, 160, 3), colour, np.uint8)
        cv2.putText(img, str(i), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        w.write(img)
    w.release()
    return path


@pytest.fixture
def silent_video(tmp_path):
    return write_video(tmp_path / "clip.avi", frames=50)


@pytest.fixture
def video_with_audio(tmp_path):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not installed")
    out = tmp_path / "tone.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=25",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "2",
                    "-shortest", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out
