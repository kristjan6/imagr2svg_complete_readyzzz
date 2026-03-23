from __future__ import annotations
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    stage: Mapped[str] = mapped_column(String(128), default="Venter i kø")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_object: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    preview_object: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    output_dxf_object: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    output_dwg_object: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    debug_objects_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
