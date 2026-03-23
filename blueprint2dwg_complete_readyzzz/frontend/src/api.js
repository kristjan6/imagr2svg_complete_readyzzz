const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function uploadImage(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form
  });

  if (!res.ok) {
    let msg = "Opplasting feilet";
    try {
      const json = await res.json();
      msg = json.detail || msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export async function getJob(jobId) {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error("Kunne ikke hente jobbstatus");
  }
  return res.json();
}

export function fileUrl(relativeOrAbsolute) {
  return relativeOrAbsolute?.startsWith("http") ? relativeOrAbsolute : `${API_BASE}${relativeOrAbsolute}`;
}
