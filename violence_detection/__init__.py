"""Two-stage violence detection in videos: an audio CNN first, then a C3D video model."""

from .cascade import Cascade, Result

__all__ = ["Cascade", "Result"]
