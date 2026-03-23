from pydantic import BaseModel

class UploadResponse(BaseModel):
    job_id: str
    status: str

class JobResponse(BaseModel):
    job_id: str
    filename: str
    status: str
    stage: str
    progress: int
    error: str | None = None
    preview_url: str | None = None
    output_svg: str | None = None
    debug_images: list[str] = []
