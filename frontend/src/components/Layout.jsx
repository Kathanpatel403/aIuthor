import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <Link to="/" className="text-lg font-semibold tracking-tight text-emerald-400 hover:text-emerald-300">
            AIuthor
          </Link>
          <nav className="flex gap-4 text-sm text-slate-400">
            <Link to="/" className="hover:text-slate-200">
              New book
            </Link>
            <Link to="/audit" className="text-indigo-400 hover:text-indigo-300 font-medium">
              Audit Suite
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
