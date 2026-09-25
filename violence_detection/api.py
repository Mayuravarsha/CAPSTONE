"""Flask API.

    POST /api/analyze   multipart form with a "file" field -> JSON Result
    GET  /api/health    {"status": "ok", "models_loaded": bool}

Configure with environment variables:
    VD_WEIGHTS_DIR   folder with final_video_model.h5 (+ final_audio_model.h5)
    VD_MAX_MB        upload limit in megabytes (default 200)
    VD_CORS_ORIGIN   allowed browser origin (default http://localhost:5173)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from .cascade import Cascade

ALLOWED = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpg", ".mpeg"}


def create_app(cascade: Cascade | None = None) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("VD_MAX_MB", 200)) * 1024 * 1024
    origin = os.environ.get("VD_CORS_ORIGIN", "http://localhost:5173")
    state = {"cascade": cascade}

    def get_cascade() -> Cascade:
        if state["cascade"] is None:          # load the TensorFlow models once, on first use
            from .models import load_trained
            audio_fn, video_fn = load_trained(os.environ.get("VD_WEIGHTS_DIR", "weights"))
            state["cascade"] = Cascade(audio_fn, video_fn)
        return state["cascade"]

    @app.after_request
    def cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_e):
        return jsonify(error=f"file larger than {app.config['MAX_CONTENT_LENGTH'] // 2**20} MB"), 413

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", models_loaded=state["cascade"] is not None)

    @app.post("/api/analyze")
    def analyze():
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            return jsonify(error="send the video as a multipart field named 'file'"), 400
        name = secure_filename(upload.filename)
        if Path(name).suffix.lower() not in ALLOWED:
            return jsonify(error=f"unsupported file type; use one of {sorted(ALLOWED)}"), 415
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            upload.save(path)
            try:
                result = get_cascade().analyse(path)
            except ValueError as e:
                return jsonify(error=str(e)), 422
        return jsonify(result.to_dict())

    return app
