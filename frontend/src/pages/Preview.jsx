import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiJson } from "../api/client.js";

export default function Preview() {
  const { bookId } = useParams();
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [sel, setSel] = useState(0);
  /** String state avoids NaN when the number input is cleared while typing */
  const [repairAfterInput, setRepairAfterInput] = useState("0");
  const [repairResult, setRepairResult] = useState(null);
  const [repairErr, setRepairErr] = useState(null);
  const [repairing, setRepairing] = useState(false);

  useEffect(() => {
    if (!bookId) return undefined;
    let cancelled = false;
    (async () => {
      try {
        const j = await apiJson(`/books/${encodeURIComponent(bookId)}/preview`);
        if (!cancelled) {
          setData(j);
          setErr(null);
          setSel(0);
        }
      } catch (ex) {
        if (!cancelled) setErr(ex instanceof Error ? ex.message : String(ex));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [bookId]);

  async function runRepair(e) {
    e.preventDefault();
    if (!bookId) return;
    setRepairErr(null);
    setRepairResult(null);
    const n = parseInt(repairAfterInput, 10);
    if (Number.isNaN(n) || n < 0) {
      setRepairErr("Enter a non-negative integer (chapter index to insert after).");
      return;
    }
    setRepairing(true);
    try {
      const r = await apiJson(`/memory/${encodeURIComponent(bookId)}/chapter-insert-repair`, {
        method: "POST",
        json: { insert_after_chapter: n },
      });
      setRepairResult(r);
    } catch (ex) {
      setRepairErr(ex instanceof Error ? ex.message : String(ex));
    } finally {
      setRepairing(false);
    }
  }

  if (!bookId) return null;

  const chapters = data?.chapters?.length ? data.chapters : null;
  const body =
    chapters && chapters[sel]
      ? chapters[sel].body
      : "";

  const totalShifted = repairResult
    ? (repairResult.shifted_facts ?? 0) +
      (repairResult.shifted_concepts ?? 0) +
      (repairResult.shifted_callbacks ?? 0)
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Preview</h1>
          <p className="text-slate-500 text-xs font-mono mt-1 break-all">{bookId}</p>
        </div>
        <Link
          to={`/downloads/${bookId}`}
          className="text-sm text-emerald-400 hover:text-emerald-300 underline-offset-4 hover:underline"
        >
          Downloads & evals →
        </Link>
      </div>

      {err && <p className="text-sm text-red-400">{err}</p>}

      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-6">
          <aside className="space-y-4">
            <h2 className="text-xs uppercase tracking-wide text-slate-500">Chapters</h2>
            {chapters && chapters.length > 0 ? (
              <ul className="space-y-1">
                {chapters.map((c, i) => (
                  <li key={c.number}>
                    <button
                      type="button"
                      onClick={() => setSel(i)}
                      className={`w-full text-left text-sm rounded-lg px-2 py-1.5 transition-colors ${
                        i === sel ? "bg-emerald-950/80 text-emerald-200" : "text-slate-400 hover:bg-slate-800"
                      }`}
                    >
                      {c.number}. {c.title}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-500">No chapters parsed from the book HTML yet.</p>
            )}

            <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 space-y-2">
              <h3 className="text-xs uppercase tracking-wide text-slate-500">Test D — memory repair</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                This runs only the <strong className="text-slate-300">in-memory repair</strong> API: it renumbers
                facts, concepts, and callbacks for chapters <em>after</em> the insert point. It does{" "}
                <strong className="text-slate-300">not</strong> add a new chapter to the book file, change the TOC in
                Markdown/PDF, or refresh the preview — those would be a separate generation/assembly step.
              </p>
              <p className="text-xs text-amber-200/90">
                If all shifted counts are <code className="text-amber-100">0</code>, memory was empty (Memory Keeper
                may not have written records for this run). The call still succeeded.
              </p>
              <form onSubmit={runRepair} className="space-y-2">
                <label className="block text-xs text-slate-400">
                  Insert after chapter index <span className="text-slate-600">(0 = before chapter 1)</span>
                  <input
                    type="number"
                    min={0}
                    step={1}
                    className="mt-1 w-full rounded bg-slate-950 border border-slate-700 px-2 py-1 text-sm text-white"
                    value={repairAfterInput}
                    onChange={(e) => setRepairAfterInput(e.target.value)}
                  />
                </label>
                <button
                  type="submit"
                  disabled={repairing}
                  className="w-full rounded bg-slate-700 hover:bg-slate-600 text-xs py-1.5 disabled:opacity-50"
                >
                  {repairing ? "Running…" : "Run repair"}
                </button>
              </form>
              {repairErr && <p className="text-xs text-red-400">{repairErr}</p>}
              {repairResult && (
                <div className="space-y-2 rounded border border-slate-700 bg-slate-950/50 p-2">
                  <p className="text-xs font-medium text-emerald-300">Repair finished</p>
                  <ul className="text-xs text-slate-300 space-y-0.5">
                    <li>Facts shifted: {repairResult.shifted_facts ?? 0}</li>
                    <li>Concepts shifted: {repairResult.shifted_concepts ?? 0}</li>
                    <li>Callbacks shifted: {repairResult.shifted_callbacks ?? 0}</li>
                  </ul>
                  {totalShifted === 0 && (
                    <p className="text-[11px] text-slate-500">No rows were updated — stores were likely empty.</p>
                  )}
                  <details className="text-[10px] text-slate-500">
                    <summary className="cursor-pointer text-slate-400 hover:text-slate-300">Raw JSON</summary>
                    <pre className="mt-1 overflow-x-auto max-h-32 whitespace-pre-wrap">{JSON.stringify(repairResult, null, 2)}</pre>
                  </details>
                </div>
              )}
            </div>
          </aside>
          <article className="rounded-xl border border-slate-800 bg-slate-900/30 p-4 min-h-[320px]">
            {chapters && chapters[sel] && (
              <h2 className="text-lg font-medium text-white mb-3">
                Chapter {chapters[sel].number}: {chapters[sel].title}
              </h2>
            )}
            <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap text-slate-300 leading-relaxed">
              {body}
            </div>
          </article>
        </div>
      )}
    </div>
  );
}
