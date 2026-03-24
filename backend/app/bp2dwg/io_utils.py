from __future__ import annotations
import cv2
import numpy as np

def load_image_from_bytes(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError("Could not decode image bytes")
    return image
