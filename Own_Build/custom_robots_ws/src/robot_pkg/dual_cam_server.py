#!/usr/bin/env python3
"""Serve the dual camera recorder page with the USB camera backend."""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, redirect, send_from_directory

APP_DIR = Path(__file__).resolve().parent
USB_BACKEND_DIR = Path.home() / "Documents" / "editing files"

if (USB_BACKEND_DIR / "usb_camera.py").exists():
    sys.path.insert(0, str(USB_BACKEND_DIR))

from usb_camera import register_usb_camera_routes  # noqa: E402

app = Flask(__name__)
register_usb_camera_routes(app)


@app.after_request
def cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "service": "dual_cam_server"})


@app.route("/")
def home():
    return redirect("/dual_camera_recorder.html")


@app.route("/<path:filename>")
def static_files(filename: str):
    return send_from_directory(APP_DIR, filename)


if __name__ == "__main__":
    print("Dual Camera: http://localhost:8000/dual_camera_recorder.html")
    print("API health:  http://localhost:8000/api/health")
    app.run(host="0.0.0.0", port=8000, debug=False)
