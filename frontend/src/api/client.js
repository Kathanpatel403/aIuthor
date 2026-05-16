const rawBase = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const API_PREFIX = (import.meta.env.VITE_API_PREFIX ?? "/api").replace(/\/$/, "");

/** @param {string} path e.g. `/generate/pipeline/start` (no /api prefix) */
export function apiUrl(path) {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${rawBase}${API_PREFIX}${p}`;
}

/**
 * @param {string} path
 * @param {{ method?: string, json?: unknown, headers?: Record<string,string> }} [opts]
 */
export async function apiJson(path, opts = {}) {
  const { method = "GET", json, headers: hdr = {} } = opts;
  /** @type {RequestInit} */
  const init = { method, headers: new Headers(hdr) };
  if (json !== undefined) {
    init.headers.set("Content-Type", "application/json");
    init.body = JSON.stringify(json);
  }
  const res = await fetch(apiUrl(path), init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      if (typeof err.detail === "string") detail = err.detail;
      else if (Array.isArray(err.detail)) detail = err.detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
      else if (err.detail != null) detail = JSON.stringify(err.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) return null;
  return res.json();
}
