const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function App() {
  const healthUrl = `${apiBase.replace(/\/$/, "")}/health`;

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-3xl font-semibold tracking-tight">AIuthor</h1>
      <p className="text-slate-400 max-w-lg text-center text-sm">
        Frontend lives in <code className="text-slate-300">frontend/</code>; API in{" "}
        <code className="text-slate-300">backend/</code>. Configure{" "}
        <code className="text-slate-300">frontend/.env</code> (see{" "}
        <code className="text-slate-300">.env.example</code>).
      </p>
      <p className="text-xs text-slate-500">API base: {apiBase}</p>
      <a
        className="text-sm text-emerald-400 hover:text-emerald-300 underline-offset-4 hover:underline"
        href={healthUrl}
        target="_blank"
        rel="noreferrer"
      >
        Backend health
      </a>
    </main>
  );
}
