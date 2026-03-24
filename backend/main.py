import os, uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
import redis
from rq import Queue

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

S3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["S3_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["S3_SECRET_ACCESS_KEY"],
    region_name=os.environ.get("S3_REGION", "us-east-1"),
)
BUCKET = os.environ["S3_BUCKET"]
REDIS_URL = os.environ["REDIS_URL"]
r = redis.from_url(REDIS_URL)
q = Queue(connection=r)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    colormode: str = "color",
    filter_speckle: int = 4,
    color_precision: int = 6,
    layer_difference: int = 16,
    corner_threshold: int = 60,
    length_threshold: float = 4.0,
    splice_threshold: int = 45,
    path_precision: int = 8,
):
    job_id = str(uuid.uuid4())
    data = await file.read()
    input_key = f"input/{job_id}/{file.filename}"
    S3.put_object(Bucket=BUCKET, Key=input_key, Body=data)

    q.enqueue(
        "worker.run_conversion",
        job_id, input_key,
        colormode, filter_speckle, color_precision,
        layer_difference, corner_threshold, length_threshold,
        splice_threshold, path_precision,
        job_id=job_id
    )
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    from rq.job import Job
    try:
        job = Job.fetch(job_id, connection=r)
        if job.is_finished:
            svg_url = f"{os.environ['S3_PUBLIC_BASE_URL']}/{BUCKET}/output/{job_id}/result.svg"
            return {"status": "done", "svg_url": svg_url}
        elif job.is_failed:
            return {"status": "failed", "error": str(job.exc_info)}
        else:
            return {"status": "processing"}
    except Exception as e:
        return {"status": "not_found", "error": str(e)}
