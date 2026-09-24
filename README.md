# Detection of Violent Content in Videos using Audio Visual Features

Capstone project at PES University (2022) that became the paper **"Detection of Violent Content in Videos using Audio Visual Features"**, which won the **2nd Best Paper Award at the 2023 IEEE ICAECIS** out of 1,300+ papers.

📄 [Read the paper on IEEE Xplore](https://doi.org/10.1109/ICAECIS58353.2023.10170034) · 🌐 [Project write-up](https://mayuravarsha.github.io/#violence-detection)

## How it works

Violence is detected in two stages so that the expensive video model does not have to run on every clip.

1. **AudioProcessor** converts the audio of a clip into a spectrogram and classifies it with a CNN (7.8M trainable parameters). If it finds violence the clip is flagged straight away.
2. **VideoProcessor** runs only when the audio model finds no violence. It uses C3D pretrained on Sports-1M as a frozen feature extractor with a small dense classifier on top (4.7M trainable out of 65.9M parameters).

## Results

| Dataset | Accuracy |
| --- | --- |
| Violent Flows | 96.18% |
| Movies | 97.58% |
| Hockey Fights | 96.85% |
| Real-Life Violence Situations (RLVS) | 95.50% |
| **Average** | **96.53%** |

Full results with precision, recall and F1 score are in the final report (`PW22_RR_02-Final_Report.pdf`).

## Repo contents

| Path | Description |
| --- | --- |
| `backend.py` | Flask API that takes an uploaded video and runs the audio and video models |
| `frontend/` | React pages for uploading a video and viewing the result |
| `PW22_RR_02-Final_Report.pdf` | Final project report |

The trained model files (`final_audio_model.h5` and `final_video_model.h5`) are not included in this repo because of their size.

## Team

Rishab K S, Pranav M R, Yashwal S Kanchan and Mayuravarsha P, under the guidance of Dr. Roopa Ravish at PES University.
