from __future__ import annotations
from dataclasses import dataclass, field
import cv2
import numpy as np

@dataclass
class PreprocessResult:
    original: np.ndarray
    gray: np.ndarray
    binary: np.ndarray
    binary_clean: np.ndarray
    text_suppressed: np.ndarray
    debug_images: dict[str, np.ndarray] = field(default_factory=dict)

def preprocess_blueprint(image: np.ndarray) -> PreprocessResult:
    debug: dict[str, np.ndarray] = {}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    debug["01_gray.png"] = gray

    denoised = cv2.fastNlMeansDenoising(gray, None, 20, 7, 21)
    debug["02_denoised.png"] = denoised

    blur = cv2.GaussianBlur(denoised, (0, 0), 25)
    normalized = cv2.divide(denoised, blur, scale=255)
    debug["03_normalized.png"] = normalized

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(normalized)
    debug["04_enhanced.png"] = enhanced

    binary = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    binary = cv2.bitwise_not(binary)
    debug["05_binary.png"] = binary

    kernel = np.ones((2, 2), np.uint8)
    binary_clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary_clean = cv2.morphologyEx(binary_clean, cv2.MORPH_CLOSE, kernel, iterations=1)
    debug["06_binary_clean.png"] = binary_clean

    horiz = cv2.morphologyEx(binary_clean, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1)))
    vert = cv2.morphologyEx(binary_clean, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25)))
    text_suppressed = cv2.bitwise_or(horiz, vert)
    debug["07_text_suppressed.png"] = text_suppressed

    return PreprocessResult(
        original=image,
        gray=enhanced,
        binary=binary,
        binary_clean=binary_clean,
        text_suppressed=text_suppressed,
        debug_images=debug,
    )
