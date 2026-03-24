from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

def convert_dxf_to_dwg(dxf_path: str, dwg_path: str, oda_executable: str) -> None:
    dxf_path = str(Path(dxf_path).resolve())
    dwg_path = str(Path(dwg_path).resolve())
    oda_executable = str(Path(oda_executable).resolve())

    if not Path(oda_executable).exists():
        raise FileNotFoundError(f"ODA executable not found: {oda_executable}")

    with tempfile.TemporaryDirectory() as in_dir, tempfile.TemporaryDirectory() as out_dir:
        src = Path(in_dir) / Path(dxf_path).name
        shutil.copy2(dxf_path, src)

        cmd = [oda_executable, in_dir, out_dir, "ACAD2018", "DWG", "0", "1", "*.DXF"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"ODA conversion failed. STDOUT: {proc.stdout} STDERR: {proc.stderr}")

        produced = Path(out_dir) / (Path(dxf_path).stem + ".dwg")
        if not produced.exists():
            raise RuntimeError("ODA completed, but DWG file was not produced.")
        shutil.copy2(produced, dwg_path)
