from __future__ import annotations
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.queue import get_queue
from app.repository import create_job, get_job, get_debug_objects
from app.schemas import JobResponse, UploadResponse
from app.storage import public_url, upload_bytes

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/health")
def health() -> dict:
    return {"ok": True}

@router.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filnavn mangler")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}:
        raise HTTPException(status_code=400, detail="Filtypen stoettes ikke. Bruk PNG, JPG, BMP, GIF eller WEBP.")
    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail=f"Filen er for stor. Maks {settings.max_upload_mb} MB")
    job_id = uuid4().hex
    safe_name = f"{job_id}/{Path(file.filename).name}"
    source_object = upload_bytes(f"uploads/{safe_name}", data, file.content_type or "application/octet-stream")
    job = create_job(db, job_id=job_id, filename=file.filename, source_object=source_object)
    get_queue().enqueue("app.worker_job.process_job", job_id, job_timeout="30m")
    return UploadResponse(job_id=job.job_id, status=job.status)

@router.get("/api/jobs/{job_id}", response_model=JobResponse)
def job_status(job_id: str, db: Session = Depends(get_db)) -> JobResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Jobb ikke funnet")
    preview_url = public_url(job.preview_object) if job.preview_object else None
    svg_url = f"/api/jobs/{job_id}/download/svg" if job.output_svg_object else None
    debug_images = [public_url(x) for x in get_debug_objects(job)]
    return JobResponse(
        job_id=job.job_id,
        filename=job.filename,
        status=job.status,
        stage=job.stage,
        progress=job.progress,
        error=job.error,
        preview_url=preview_url,
        output_svg=svg_url,
        debug_images=debug_images,
    )

@router.get("/api/jobs/{job_id}/download/svg")
def download_svg(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if job is None or not job.output_svg_object:
        raise HTTPException(status_code=404, detail="SVG ikke funnet")
    return RedirectResponse(public_url(job.output_svg_object))
