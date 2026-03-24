import React, { useEffect, useRef, useState } from "react";
import { getJob, uploadBlueprint, fileUrl } from "./api";

export default function App() {
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState("");
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [showDebug, setShowDebug] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!job?.job_id) return;
    if (job.status === "completed" || job.status === "failed") return;

    const timer = setInterval(async () => {
      try {
        const next = await getJob(job.job_id);
        setJob(next);
      } catch (err) {
        setError(err.message || "Statusoppdatering feilet");
      }
    }, 1200);

    return () => clearInterval(timer);
  }, [job]);

  async function handleFile(file) {
    setError("");
    setJob(null);
    setShowDebug(false);
    setFileName(file.name);

    try {
      const created = await uploadBlueprint(file);
      const status = await getJob(created.job_id);
      setJob(status);
    } catch (err) {
      setError(err.message || "Opplasting feilet");
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  function onChange(e) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Blueprint → DXF</h1>
        <p className="subtitle">
          Last opp blueprint, skannet tegning eller PDF. Se preview, følg status, og last ned ferdig fil når jobben er klar.
        </p>

        <div
          className={`dropzone ${dragActive ? "active" : ""}`}
          onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".png,.jpg,.jpeg,.tif,.tiff,.bmp,.pdf"
            className="hidden-input"
            onChange={onChange}
          />
          <div className="dropzone-title">Dra fil hit</div>
          <div className="dropzone-text">eller klikk for å velge</div>
        </div>

        {fileName && (
          <div className="panel">
            <div><strong>Fil:</strong> {fileName}</div>
          </div>
        )}

        {job?.preview_url && (
          <div className="panel">
            <div className="section-title">Forhåndsvisning</div>
            <img className="preview-image" src={fileUrl(job.preview_url)} alt="Preview" />
          </div>
        )}

        {job && (
          <div className="panel">
            <div><strong>Status:</strong> {job.status}</div>
            <div><strong>Steg:</strong> {job.stage}</div>

            <div className="progress">
              <div className="progress-bar" style={{ width: `${job.progress}%` }} />
            </div>

            <div className="progress-text">{job.progress}%</div>

            {job.error && <div className="warning">{job.error}</div>}

            {job.status === "completed" && (
              <div className="downloads">
                {job.output_dxf && <a className="button" href={fileUrl(job.output_dxf)}>Last ned DXF</a>}
                {job.output_dwg && <a className="button secondary" href={fileUrl(job.output_dwg)}>Last ned DWG</a>}
              </div>
            )}
          </div>
        )}

        {job?.debug_images?.length > 0 && (
          <div className="panel">
            <div className="debug-header">
              <div className="section-title">Debug-bilder</div>
              <button className="toggle-button" type="button" onClick={() => setShowDebug(v => !v)}>
                {showDebug ? "Skjul" : "Vis"}
              </button>
            </div>

            {showDebug && (
              <div className="debug-grid">
                {job.debug_images.map((url) => (
                  <a key={url} className="debug-card" href={fileUrl(url)} target="_blank" rel="noreferrer">
                    <img src={fileUrl(url)} alt={url} />
                    <div className="debug-label">{url.split("/").pop()}</div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}

        {error && <div className="error">{error}</div>}
      </div>
    </div>
  );
}
