import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiJson } from "../api/client.js";

const POLL_MS = 2500;

export default function Pipeline() {
  const { bookId } = useParams();
  const [status, setStatus] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!bookId) return undefined;
    let cancelled = false;

    async function tick() {
      try {
        const s = await apiJson(`/generate/pipeline/status/${encodeURIComponent(bookId)}`);
        if (!cancelled) {
          setStatus(s);
          setErr(null);
        }
      } catch (ex) {
        if (!cancelled) setErr(ex instanceof Error ? ex.message : String(ex));
      }
    }

    tick();
    const id = window.setInterval(tick, POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [bookId]);

  if (!bookId) return null;

  const done = status?.status === "done";
  const failed = status?.status === "error";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Pipeline</h1>
        <p className="text-slate-500 text-xs font-mono mt-1 break-all">{bookId}</p>
      </div>

      {err && <p className="text-sm text-red-400 border border-red-900/50 rounded-lg px-3 py-2 bg-red-950/30">{err}</p>}

      {status && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 space-y-3 text-sm">
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            <span>
              <span className="text-slate-500">Status</span>{" "}
              <span className={failed ? "text-red-400" : done ? "text-emerald-400" : "text-amber-300"}>
                {status.status}
              </span>
            </span>
            {status.stage && (
              <span>
                <span className="text-slate-500">Stage</span> <span className="text-slate-200">{status.stage}</span>
              </span>
            )}
            {status.current_agent && (
              <span>
                <span className="text-slate-500">Agent</span>{" "}
                <span className="text-slate-200">{status.current_agent}</span>
              </span>
            )}
          </div>
          {status.total_chapters != null && (
            <p className="text-slate-400">
              {done ? (
                <>
                  All <span className="text-slate-200">{status.total_chapters}</span> chapters finished.
                </>
              ) : (
                <>
                  Working on chapter{" "}
                  <span className="text-slate-200">
                    {Math.min((status.chapter_index ?? 0) + 1, status.total_chapters)}
                  </span>{" "}
                  of {status.total_chapters}.
                </>
              )}
            </p>
          )}
          {status.brief_summary && (
            <p className="text-slate-500 text-xs">
              {status.brief_summary.topic} · {status.brief_summary.genre} · {status.brief_summary.tonality}
            </p>
          )}
          {failed && status.error && (
            <pre className="text-xs text-red-300 whitespace-pre-wrap bg-black/30 rounded-lg p-3 overflow-x-auto">
              {status.error}
            </pre>
          )}
        </div>
      )}

      {done && (
        <div className="flex flex-wrap gap-3">
          <Link
            to={`/preview/${bookId}`}
            className="inline-flex rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 px-4 py-2 text-sm"
          >
            Preview
          </Link>
          <Link
            to={`/downloads/${bookId}`}
            className="inline-flex rounded-lg bg-emerald-700 hover:bg-emerald-600 px-4 py-2 text-sm font-medium text-white"
          >
            Downloads & evals
          </Link>
        </div>
      )}

      <p className="text-xs text-slate-600">Polling every {POLL_MS / 1000}s. Job state is in-memory on the API server.</p>
    </div>
  );
}
