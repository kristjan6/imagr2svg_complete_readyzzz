from __future__ import annotations
from dataclasses import dataclass, field
import cv2
import numpy as np

@dataclass
class LineEntity:
    x1: float
    y1: float
    x2: float
    y2: float
    layer: str = "LINES"

@dataclass
class GeometryResult:
    lines: list[LineEntity] = field(default_factory=list)

def extract_geometry(binary: np.ndarray, text_suppressed: np.ndarray, scale: float = 1.0) -> GeometryResult:
    result = GeometryResult()

    line_img = cv2.HoughLinesP(
        text_suppressed,
        rho=1,
        theta=np.pi / 180,
        threshold=70,
        minLineLength=30,
        maxLineGap=10,
    )

    if line_img is not None:
        for l in line_img[:, 0]:
            x1, y1, x2, y2 = map(float, l.tolist())
            result.lines.append(LineEntity(x1 * scale, y1 * scale, x2 * scale, y2 * scale, "LINES"))

    # Deduplicate roughly
    unique = []
    for ln in result.lines:
        found = False
        for ex in unique:
            if abs(ln.x1 - ex.x1) < 4 and abs(ln.y1 - ex.y1) < 4 and abs(ln.x2 - ex.x2) < 4 and abs(ln.y2 - ex.y2) < 4:
                found = True
                break
        if not found:
            unique.append(ln)
    result.lines = unique
    return result
