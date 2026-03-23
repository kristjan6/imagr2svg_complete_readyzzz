from __future__ import annotations
import io
import os
import subprocess
import tempfile

import cv2
import numpy as np
from PIL import Image

from app.config import settings
from app.db import SessionLocal
from app.repository import get_job, set_debug_objects, update_job
from app.storage import download_bytes, upload_bytes


def _encode_png(image) -> bytes:
    ok, buf = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Could not encode PNG")
    return buf.tobytes()


def _image_to_svg(image_bgr) -> str:
    """Convert a BGR OpenCV image to an SVG string using potrace."""
    # Convert to grayscale then binary
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    with tempfile.TemporaryDirectory() as tmp:
        bmp_path = os.path.join(tmp, "input.bmp")
        svg_path = os.path.join(tmp, "output.svg")

        # Save as BMP for potrace
        pil_img = Image.fromarray(binary)
        pil_img.save(bmp_path)

        # Run potrace to convert BMP -> SVG
        result = subprocess.run(
            ["potrace", "--svg", "-o", svg_path, bmp_path],
            capture_output=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"potrace failed: {result.stderr.decode()}")

        with open(svg_path, "r", encoding="utf-8") as f:
            return f.read()


def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = get_job(db, job_id)
        if job is None:
            raise ValueError(f"Job not found: {job_id}")

        update_job(db, job_id, status="processing", stage="Laster inn bilde", progress=5, error=None)
        raw = download_bytes(job.source_object)

        # Decode image
        arr = np.frombuffer(raw, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError("Kunne ikke lese bildefilen. Sjekk at det er et gyldig bilde.")

        # Create and upload preview
        preview = image.copy()
        h, w = preview.shape[:2]
        max_w = 1400
        scale = min(1.0, max_w / float(w))
        if scale < 1.0:
            preview = cv2.resize(preview, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        preview_key = f"jobs/{job_id}/preview.png"
        upload_bytes(preview_key, _encode_png(preview), "image/png")
        update_job(db, job_id, stage="Forbehandler bilde", progress=30, preview_object=preview_key)

        # Debug: save grayscale and binary threshold images
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        debug_keys = []
        gray_key = f"jobs/{job_id}/debug/grayscale.png"
        binary_key = f"jobs/{job_id}/debug/binary.png"
        upload_bytes(gray_key, _encode_png(gray), "image/png")
        upload_bytes(binary_key, _encode_png(binary), "image/png")
        debug_keys = [gray_key, binary_key]
        set_debug_objects(db, job_id, debug_keys)

        update_job(db, job_id, stage="Vektoriserer til SVG", progress=60)

        # Convert to SVG
        svg_content = _image_to_svg(image)
        svg_bytes = svg_content.encode("utf-8")

        update_job(db, job_id, stage="Lagrer SVG", progress=90)
        svg_key = f"jobs/{job_id}/result.svg"
        upload_bytes(svg_key, svg_bytes, "image/svg+xml")

        update_job(
            db,
            job_id,
            status="completed",
            stage="Ferdig",
            progress=100,
            output_svg_object=svg_key,
        )
    except Exception as exc:
        update_job(db, job_id, status="failed", stage="Feilet", error=str(exc))
        raise
    finally:
        db.close()
