from __future__ import annotations
import json

from sqlalchemy.orm import Session

from app.models import Job

def create_job(db: Session, job_id: str, filename: str, source_object: str) -> Job:
    job = Job(
        job_id=job_id,
        filename=filename,
        source_object=source_object,
        status="queued",
        stage="Venter i kø",
        progress=0,
        debug_objects_json="[]",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id)

def update_job(db: Session, job_id: str, **fields) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise ValueError(f"Job not found: {job_id}")
    for key, value in fields.items():
        setattr(job, key, value)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def set_debug_objects(db: Session, job_id: str, objects: list[str]) -> Job:
    return update_job(db, job_id, debug_objects_json=json.dumps(objects))

def get_debug_objects(job: Job) -> list[str]:
    if not job.debug_objects_json:
        return []
    try:
        return json.loads(job.debug_objects_json)
    except Exception:
        return []
