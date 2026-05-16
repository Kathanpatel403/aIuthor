import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiJson } from "../api/client.js";

const TONALITIES = ["conversational", "academic", "storyteller", "motivational", "witty"];

export default function Home() {
  const navigate = useNavigate();
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    topic: "Short introduction to vector databases for developers",
    reader_profile: "Software engineers comfortable with Python who are new to retrieval systems",
    genre: "nonfiction",
    tonality: "conversational",
    chapter_count: 2,
    words_per_chapter: 400,
    constraints: "",
  });

  function onChange(e) {
    const { name, value, type } = e.target;
    setForm((f) => ({
      ...f,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const payload = {
        topic: form.topic.trim(),
        reader_profile: form.reader_profile.trim(),
        genre: form.genre.trim(),
        tonality: form.tonality,
        chapter_count: form.chapter_count,
        words_per_chapter: form.words_per_chapter,
        constraints: form.constraints.trim() || null,
      };
      const data = await apiJson("/generate/pipeline/start", { method: "POST", json: payload });
      navigate(`/pipeline/${data.book_id}`);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : String(ex));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Start a book</h1>
        <p className="text-slate-400 text-sm mt-1 max-w-2xl">
          Submits your brief to the backend and queues a full pipeline run. You will be taken to a live status page
          while agents plan, research, write, and assemble exports.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-5 max-w-xl">
        <label className="block space-y-1">
          <span className="text-xs uppercase tracking-wide text-slate-500">Topic</span>
          <textarea
            name="topic"
            required
            minLength={3}
            rows={2}
            className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            value={form.topic}
            onChange={onChange}
          />
        </label>
        <label className="block space-y-1">
          <span className="text-xs uppercase tracking-wide text-slate-500">Reader profile</span>
          <textarea
            name="reader_profile"
            required
            minLength={3}
            rows={2}
            className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            value={form.reader_profile}
            onChange={onChange}
          />
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className="block space-y-1">
            <span className="text-xs uppercase tracking-wide text-slate-500">Genre</span>
            <input
              name="genre"
              required
              minLength={2}
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              value={form.genre}
              onChange={onChange}
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs uppercase tracking-wide text-slate-500">Tonality</span>
            <select
              name="tonality"
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              value={form.tonality}
              onChange={onChange}
            >
              {TONALITIES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <label className="block space-y-1">
            <span className="text-xs uppercase tracking-wide text-slate-500">Chapters</span>
            <input
              name="chapter_count"
              type="number"
              min={1}
              max={50}
              required
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              value={form.chapter_count}
              onChange={onChange}
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs uppercase tracking-wide text-slate-500">Words / chapter</span>
            <input
              name="words_per_chapter"
              type="number"
              min={200}
              max={15000}
              required
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              value={form.words_per_chapter}
              onChange={onChange}
            />
          </label>
        </div>
        <label className="block space-y-1">
          <span className="text-xs uppercase tracking-wide text-slate-500">Constraints (optional)</span>
          <textarea
            name="constraints"
            rows={2}
            className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            value={form.constraints}
            onChange={onChange}
            placeholder="e.g. no medical claims, EU-focused compliance notes only"
          />
        </label>

        {err && (
          <p className="text-sm text-red-400 bg-red-950/40 border border-red-900/60 rounded-lg px-3 py-2">{err}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 transition-colors"
        >
          {loading ? "Starting…" : "Generate book"}
        </button>
      </form>
    </div>
  );
}
