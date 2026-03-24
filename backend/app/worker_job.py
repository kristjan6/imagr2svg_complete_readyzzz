from __future__ import annotations
import io
import os
import tempfile

import cv2
import fitz

from app.config import settings
from app.db import SessionLocal
from app.repository import get_job, set_debug_objects, update_job
from app.storage import download_bytes, upload_bytes
from app.bp2dwg.io_utils import load_image_from_bytes
from app.bp2dwg.pdf_utils import render_pdf_page_from_bytes
from app.bp2dwg.preprocess import preprocess_blueprint
from app.bp2dwg.vectorize import extract_geometry
from app.bp2dwg.dxf_export import export_dxf
from app.bp2dwg.dwg_convert import convert_dxf_to_dwg

def _encode_png(image) -> bytes:
    ok, buf = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Could not encode PNG")
    return buf.tobytes()

def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = get_job(db, job_id)
        if job is None:
            raise ValueError(f"Job not found: {job_id}")

        update_job(db, job_id, status="processing", stage="Laster inn fil", progress=5, error=None)

        raw = download_bytes(job.source_object)
        filename = job.filename.lower()

        if filename.endswith(".pdf"):
            image = render_pdf_page_from_bytes(raw, page_index=0, dpi=220)
        else:
            image = load_image_from_bytes(raw)

        preview = image.copy()
        h, w = preview.shape[:2]
        max_w = 1400
        scale = min(1.0, max_w / float(w))
        if scale < 1.0:
            preview = cv2.resize(preview, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        preview_key = f"jobs/{job_id}/preview.png"
        upload_bytes(preview_key, _encode_png(preview), "image/png")
        update_job(db, job_id, stage="Forbehandler tegning", progress=20, preview_object=preview_key)

        prep = preprocess_blueprint(image)

        debug_keys = []
        for name, debug_img in prep.debug_images.items():
            key = f"jobs/{job_id}/debug/{name}"
            upload_bytes(key, _encode_png(debug_img), "image/png")
            debug_keys.append(key)

        set_debug_objects(db, job_id, debug_keys)
        update_job(db, job_id, stage="Vektoriserer geometri", progress=60)

        geometry = extract_geometry(prep.binary_clean, text_suppressed=prep.text_suppressed, scale=1.0)

        update_job(db, job_id, stage="Lager DXF", progress=85)
        with tempfile.TemporaryDirectory() as tmp:
            dxf_path = os.path.join(tmp, "result.dxf")
            export_dxf(dxf_path, geometry, image_height_px=image.shape[0], scale=1.0)
            with open(dxf_path, "rb") as f:
                dxf_key = f"jobs/{job_id}/result.dxf"
                upload_bytes(dxf_key, f.read(), "application/dxf")
            dwg_key = None
            if settings.enable_dwg and settings.oda_executable:
                try:
                    dwg_path = os.path.join(tmp, "result.dwg")
                    convert_dxf_to_dwg(dxf_path, dwg_path, settings.oda_executable)
                    with open(dwg_path, "rb") as f:
                        dwg_key = f"jobs/{job_id}/result.dwg"
                        upload_bytes(dwg_key, f.read(), "application/octet-stream")
                except Exception as exc:
                    update_job(db, job_id, error=f"DXF er klar, men DWG feilet: {exc}")

        update_job(
            db,
            job_id,
            status="completed",
            stage="Ferdig",
            progress=100,
            output_dxf_object=dxf_key,
            output_dwg_object=dwg_key,
        )
    except Exception as exc:
        update_job(db, job_id, status="failed", stage="Feilet", error=str(exc))
        raise
    finally:
        db.close()
