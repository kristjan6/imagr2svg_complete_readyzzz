from __future__ import annotations
import ezdxf

def _cad_y(image_height_px: float, y_px: float, scale: float) -> float:
    return (image_height_px * scale) - y_px

def export_dxf(output_path: str, geometry, image_height_px: int, scale: float = 1.0) -> None:
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()
    if "LINES" not in {layer.dxf.name for layer in doc.layers}:
        doc.layers.add("LINES", color=7)

    for line in geometry.lines:
        msp.add_line(
            (line.x1, _cad_y(image_height_px, line.y1, scale)),
            (line.x2, _cad_y(image_height_px, line.y2, scale)),
            dxfattribs={"layer": line.layer},
        )

    doc.saveas(output_path)
