"""Architecture checks against the numbers in the paper (need TensorFlow)."""

import numpy as np
import pytest

tf = pytest.importorskip("tensorflow")

from violence_detection import models  # noqa: E402


def trainable(model):
    return sum(int(np.prod(w.shape)) for w in model.trainable_weights)


def test_video_head_has_4_7m_trainable_parameters():
    m = models.build_video_model()
    assert trainable(m) == 4096 * 1024 + 1024 + 1024 * 512 + 512 + 512 + 1 == 4_720_641
    assert m.output_shape == (None, 1)


def test_c3d_up_to_fc6_matches_sports1m_layout():
    c3d = models.build_c3d()
    assert c3d.get_layer("pool5").output_shape == (None, 1, 4, 4, 512)
    assert c3d.get_layer("fc6").output_shape == (None, 4096)
    assert c3d.output_shape == (None, 487)


def test_audio_model_outputs_two_probabilities():
    m = models.build_audio_model(time_frames=256)
    out = m(np.zeros((2, 256, 129), np.float32), training=False).numpy()
    assert out.shape == (2, 2)
    np.testing.assert_allclose(out.sum(axis=1), 1, rtol=1e-5)
