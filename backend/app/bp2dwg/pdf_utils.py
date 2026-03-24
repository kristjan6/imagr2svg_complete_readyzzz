from __future__ import annotations
import fitz
import numpy as np
import cv2

def render_pdf_page_from_bytes(data: bytes, page_index: int = 0, dpi: int = 220) -> np.ndarray:
    doc = fitz.open(stream=data, filetype="pdf")
    if page_index < 0 or page_index >= len(doc):
        raise IndexError("PDF page out of range")
    page = doc.load_page(page_index)
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 3:
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if pix.n == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    raise RuntimeError("Unsupported PDF pixel format")
