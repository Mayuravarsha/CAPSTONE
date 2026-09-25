"""Keras model definitions (from the project report) and loaders for trained weights.

TensorFlow is imported lazily so the rest of the package (and its tests)
work without it.

* Audio CNN: three Conv2D/BatchNorm/MaxPool blocks on the spectrogram, then
  Dense(64) and a 2-way softmax (non-violent, violent). The report's listing
  ends in Dense(1, softmax), which always outputs 1.0, and never adds its
  Dropout layers to the model. The deployed server read two outputs, so this
  definition follows the deployed model: Dense(2, softmax), with the dropout
  actually applied.
* Video model: C3D pretrained on Sports-1M, frozen up to fc6 (4096-d
  features), followed by Dropout -> Dense(1024) -> Dropout -> Dense(512) ->
  Dropout -> Dense(1, sigmoid). Only the head (4.72M parameters) is trained.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .audio import FFT_LENGTH, TIME_FRAMES
from .video import CLIP_LENGTH, FRAME_SIZE


def _tf():
    import tensorflow as tf  # noqa: PLC0415
    return tf


def build_audio_model(time_frames: int = TIME_FRAMES):
    tf = _tf()
    L, reg = tf.keras.layers, tf.keras.regularizers.l1_l2(l1=0.01, l2=0.01)
    model = tf.keras.Sequential([L.Input((time_frames, FFT_LENGTH // 2 + 1)),
                                 L.Reshape((time_frames, FFT_LENGTH // 2 + 1, 1))])
    for filters, kernel, pool in ((64, 3, 3), (64, 3, 3), (32, 2, 2)):
        model.add(L.Conv2D(filters, kernel, activation="relu", kernel_regularizer=reg))
        model.add(L.BatchNormalization())
        model.add(L.MaxPooling2D(pool, strides=2, padding="same"))
        model.add(L.Dropout(0.3))
    model.add(L.Flatten())
    model.add(L.Dense(64, activation="relu"))
    model.add(L.Dropout(0.2))
    model.add(L.Dense(2, activation="softmax"))
    return model


def build_c3d():
    """C3D (Tran et al., 2015) as trained on Sports-1M, 487 classes."""
    tf = _tf()
    L = tf.keras.layers
    conv = lambda f, name: L.Conv3D(f, 3, activation="relu", padding="same", name=name)  # noqa: E731
    pool = lambda k, name: L.MaxPooling3D(k, strides=k, padding="valid", name=name)     # noqa: E731
    return tf.keras.Sequential([
        L.Input((CLIP_LENGTH, FRAME_SIZE, FRAME_SIZE, 3)),
        conv(64, "conv1"), pool((1, 2, 2), "pool1"),
        conv(128, "conv2"), pool((2, 2, 2), "pool2"),
        conv(256, "conv3a"), conv(256, "conv3b"), pool((2, 2, 2), "pool3"),
        conv(512, "conv4a"), conv(512, "conv4b"), pool((2, 2, 2), "pool4"),
        conv(512, "conv5a"), conv(512, "conv5b"),
        L.ZeroPadding3D(((0, 0), (0, 1), (0, 1)), name="zeropad5"), pool((2, 2, 2), "pool5"),
        L.Flatten(),
        L.Dense(4096, activation="relu", name="fc6"), L.Dropout(0.5),
        L.Dense(4096, activation="relu", name="fc7"), L.Dropout(0.5),
        L.Dense(487, activation="softmax", name="fc8"),
    ])


def build_video_model(sports1m_weights: str | Path | None = None):
    tf = _tf()
    L = tf.keras.layers
    c3d = build_c3d()
    if sports1m_weights:
        c3d.load_weights(str(sports1m_weights))
    features = tf.keras.Model(c3d.inputs, c3d.get_layer("fc6").output)
    features.trainable = False
    x = L.Dropout(0.5)(features.output)
    x = L.Dense(1024, activation="relu", name="fc7-alt")(x)
    x = L.Dropout(0.5)(x)
    x = L.Dense(512, activation="relu", name="fc8-alt")(x)
    x = L.Dropout(0.5)(x)
    out = L.Dense(1, activation="sigmoid", name="violence")(x)
    model = tf.keras.Model(features.inputs, out)
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model


def load_trained(weights_dir: str | Path):
    """Load final_audio_model.h5 (optional) and final_video_model.h5 as plain callables."""
    tf = _tf()
    weights_dir = Path(weights_dir)
    video = tf.keras.models.load_model(weights_dir / "final_video_model.h5", compile=False)
    audio_path = weights_dir / "final_audio_model.h5"
    audio = tf.keras.models.load_model(audio_path, compile=False) if audio_path.exists() else None

    def video_fn(clips: np.ndarray) -> np.ndarray:
        return video.predict(clips, verbose=0).ravel()

    def audio_fn(spec: np.ndarray) -> float:
        out = audio.predict(spec, verbose=0).ravel()
        return float(out[-1])               # [P(non-violent), P(violent)]

    return (audio_fn if audio else None), video_fn
