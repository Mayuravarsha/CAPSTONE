Put the trained models here (not included in the repository because of their size):

| File | Model |
| --- | --- |
| `final_video_model.h5` | C3D (Sports-1M, frozen to fc6) + trained dense head (required) |
| `final_audio_model.h5` | spectrogram CNN, 2-way softmax (optional; without it only the video stage runs) |

To retrain the video head, start from the Sports-1M C3D weights (`weights.h5` in the
report) and `violence_detection.models.build_video_model(sports1m_weights=...)`.
