import os, vtracer, boto3

S3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["S3_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["S3_SECRET_ACCESS_KEY"],
    region_name=os.environ.get("S3_REGION", "us-east-1"),
)
BUCKET = os.environ["S3_BUCKET"]

def run_conversion(
    job_id, input_key,
    colormode, filter_speckle, color_precision,
    layer_difference, corner_threshold, length_threshold,
    splice_threshold, path_precision
):
    obj = S3.get_object(Bucket=BUCKET, Key=input_key)
    img_bytes = obj["Body"].read()

    ext = input_key.rsplit(".", 1)[-1].lower()
    fmt = "jpeg" if ext in ("jpg", "jpeg") else ext

    svg_str = vtracer.convert_raw_image_to_svg(
        img_bytes,
        img_format=fmt,
        colormode=colormode,
        hierarchical="stacked",
        mode="spline",
        filter_speckle=filter_speckle,
        color_precision=color_precision,
        layer_difference=layer_difference,
        corner_threshold=corner_threshold,
        length_threshold=length_threshold,
        splice_threshold=splice_threshold,
        path_precision=path_precision,
    )
    out_key = f"output/{job_id}/result.svg"
    S3.put_object(
        Bucket=BUCKET, Key=out_key,
        Body=svg_str.encode("utf-8"),
        ContentType="image/svg+xml"
    )
