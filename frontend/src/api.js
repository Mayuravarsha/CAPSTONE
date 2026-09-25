const BASE = import.meta.env.VITE_API_URL ?? "";

export async function analyzeVideo(file, { signal } = {}) {
  const body = new FormData();
  body.append("file", file);
  const res = await fetch(`${BASE}/api/analyze`, { method: "POST", body, signal });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error ?? `server returned ${res.status}`);
  return data;
}
