import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiJson, apiUrl } from "../api/client.js";

const TONALITIES = ["conversational", "academic", "storyteller", "motivational", "witty"];

export default function Downloads() {
  const { bookId } = useParams();
  const [exportsData, setExportsData] = useState(null);
  const [trace, setTrace] = useState(null);
  const [evalReport, setEvalReport] = useState(null);
  const [tonality, setTonality] = useState("conversational");
  const [err, setErr] = useState(null);
  const [evalLoading, setEvalLoading] = useState(false);

  useEffect(() => {
    if (!bookId) return undefined;
    let cancelled = false;
    (async () => {
      try {
        const [ex, tr] = await Promise.all([
          apiJson(`/books/${encodeURIComponent(bookId)}/exports`),
          apiJson(`/traces/${encodeURIComponent(bookId)}`).catch(() => null),
        ]);
        if (!cancelled) {
          setExportsData(ex);
          setTrace(tr);
          setErr(null);
        }
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [bookId]);

  async function loadEvalReport() {
    if (!bookId) return;
    try {
      const r = await apiJson(`/evals/${encodeURIComponent(bookId)}/report`);
      setEvalReport(r);
    } catch {
      setEvalReport(null);
    }
  }

  useEffect(() => {
    loadEvalReport();
  }, [bookId]);

  async function runEvals() {
    if (!bookId) return;
    setEvalLoading(true);
    setErr(null);
    try {
      const q = new URLSearchParams({ target_tonality: tonality });
      const r = await apiJson(`/evals/${encodeURIComponent(bookId)}?${q}`, { method: "POST", json: {} });
      setEvalReport(r);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setEvalLoading(false);
    }
  }

  if (!bookId) return null;

  const downloads = exportsData?.downloads;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Downloads</h1>
          <p className="text-slate-500 text-xs font-mono mt-1 break-all">{bookId}</p>
        </div>
        <Link to={`/preview/${bookId}`} className="text-sm text-emerald-400 hover:text-emerald-300 underline-offset-4 hover:underline">
          ← Preview
        </Link>
      </div>

      {err && <p className="text-sm text-red-400">{err}</p>}

      {downloads && (
        <section className="space-y-3">
          <h2 className="text-sm font-medium text-slate-300">Files</h2>
          <ul className="flex flex-wrap gap-3">
            {["pdf", "docx"].map((k) =>
              downloads[k] ? (
                <li key={k}>
                  <a
                    href={downloads[k]}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex rounded-lg border border-slate-600 bg-slate-800 hover:bg-slate-700 px-4 py-2 text-sm uppercase"
                  >
                    {k}
                  </a>
                </li>
              ) : null,
            )}
          </ul>
          <p className="text-xs text-slate-600">
            Served from <code className="text-slate-500">{apiUrl("/media/sample-books/…")}</code>
          </p>
        </section>
      )}

      <section className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
        <h2 className="text-sm font-medium text-slate-300">Evaluation suite</h2>
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-xs text-slate-500">
            Target tonality
            <select
              className="mt-1 block rounded-lg bg-slate-950 border border-slate-700 px-2 py-1.5 text-sm text-white"
              value={tonality}
              onChange={(e) => setTonality(e.target.value)}
            >
              {TONALITIES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={runEvals}
            disabled={evalLoading}
            className="rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-sm font-medium px-4 py-2 text-white"
          >
            {evalLoading ? "Running evals…" : "Run evals"}
          </button>
          <button type="button" onClick={loadEvalReport} className="text-xs text-slate-500 hover:text-slate-300 underline">
            Refresh saved report
          </button>
        </div>
        {evalReport && (
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-slate-500">Overall</span>{" "}
              <span className="text-emerald-400 font-mono">{(evalReport.overall_score * 100).toFixed(1)}%</span>
            </p>
            <ul className="grid sm:grid-cols-2 gap-2">
              {evalReport.dimensions?.map((d) => (
                <li key={d.name} className="rounded border border-slate-800 px-2 py-1.5 text-xs">
                  <span className="text-slate-400">{d.name}</span>{" "}
                  <span className="text-slate-200 font-mono">{(d.score * 100).toFixed(0)}%</span>
                  {d.detail && <p className="text-slate-600 mt-1 line-clamp-2">{d.detail}</p>}
                </li>
              ))}
            </ul>
            {evalReport.failure_analysis?.length > 0 && (
              <ul className="text-xs text-amber-300/90 list-disc pl-4 space-y-1">
                {evalReport.failure_analysis.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>

      {trace?.manifest && (
        <section className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-2 text-sm">
          <h2 className="text-sm font-medium text-slate-300">Trace bundle</h2>
          <p className="text-xs text-slate-500">
            Run started <span className="text-slate-400">{trace.manifest.started_at}</span> · events{" "}
            {trace.manifest.counts?.trace_events}
          </p>
          <a
            href={apiUrl(`/traces/${encodeURIComponent(bookId)}`)}
            target="_blank"
            rel="noreferrer"
            className="text-emerald-400 text-sm hover:underline"
          >
            Open trace JSON summary
          </a>
        </section>
      )}
    </div>
  );
}
