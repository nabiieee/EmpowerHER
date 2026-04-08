import { useCallback, useState } from "react";
import { postMatchQuery, type MatchResponse } from "./api";

const EXAMPLE_PROMPTS = [
  "I'm a bootcamp grad pivoting from retail into UX research in health tech.",
  "Senior PM returning from parental leave, want flexible remote roles in fintech.",
  "New grad in CS looking for a mentor in backend engineering and interview prep.",
];

function SparklesIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.847a4.5 4.5 0 003.09 3.09L15.75 12l-2.847.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
    </svg>
  );
}

export default function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResponse | null>(null);

  const runMatch = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await postMatchQuery(trimmed);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, [input, loading]);

  return (
    <div className="min-h-screen text-slate-900">
      <header className="border-b border-rose-100/80 bg-white/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-coral-400 to-orchid-600 text-white shadow-md shadow-rose-200/50">
              <SparklesIcon />
            </div>
            <div>
              <p className="font-display text-lg font-semibold tracking-tight text-rose-950">
                EmpowerHer
              </p>
              <p className="text-xs text-slate-500">Mentors &amp; roles, matched to your story</p>
            </div>
          </div>
          <span className="hidden rounded-full bg-blush-100 px-3 py-1 text-xs font-medium text-rose-900 sm:inline">
            Natural language · AI-guided
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <section className="mb-12 text-center sm:text-left">
          <h1 className="font-display text-3xl font-semibold leading-tight text-rose-950 sm:text-4xl">
            Tell us where you are — we’ll connect you with guides and opportunities.
          </h1>
          <p className="mt-4 max-w-2xl text-slate-600">
            Describe your goals, constraints, and background in your own words. Our LangGraph workflow interprets your
            intent, queries Supabase for mentors and jobs, and explains why each match fits.
          </p>
        </section>

        <section className="rounded-2xl border border-rose-100 bg-white/90 p-5 shadow-lg shadow-rose-100/40 sm:p-8">
          <label htmlFor="nl-input" className="mb-2 block text-sm font-medium text-slate-700">
            Your message
          </label>
          <textarea
            id="nl-input"
            rows={5}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Example: I'm transitioning from teaching to product design and need interview practice plus remote-friendly roles…"
            className="w-full resize-y rounded-xl border border-rose-100 bg-blush-50/50 px-4 py-3 text-slate-900 placeholder:text-slate-400 focus:border-orchid-500 focus:outline-none focus:ring-2 focus:ring-orchid-500/30"
          />
          <div className="mt-3 flex flex-wrap gap-2">
            {EXAMPLE_PROMPTS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setInput(p)}
                className="rounded-full border border-rose-100 bg-white px-3 py-1 text-left text-xs text-slate-600 transition hover:border-orchid-300 hover:bg-purple-50"
              >
                Try: {p.slice(0, 48)}…
              </button>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={runMatch}
              disabled={loading || !input.trim()}
              className="inline-flex items-center gap-2 rounded-xl bg-linear-to-r from-coral-500 to-orchid-600 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-rose-200/60 transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <SparklesIcon />
              {loading ? "Matching…" : "Find mentors & jobs"}
            </button>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>
        </section>

        {result && (
          <div className="mt-10 space-y-10">
            <section className="rounded-2xl border border-rose-100 bg-white/95 p-6 shadow-md">
              <h2 className="font-display text-xl font-semibold text-rose-950">How we understood you</h2>
              <p className="mt-3 text-slate-700">{result.summary}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {result.interpreted_goals.map((g) => (
                  <span key={g} className="rounded-full bg-blush-100 px-3 py-1 text-xs font-medium text-rose-900">
                    {g}
                  </span>
                ))}
              </div>
              {result.skills.length > 0 && (
                <p className="mt-3 text-sm text-slate-600">
                  <span className="font-medium text-slate-800">Signals: </span>
                  {result.skills.join(" · ")}
                </p>
              )}
            </section>

            <section>
              <h2 className="font-display text-xl font-semibold text-rose-950">Career guides</h2>
              <ul className="mt-4 grid gap-4 sm:grid-cols-2">
                {result.mentors.map((m) => (
                  <li
                    key={m.id}
                    className="rounded-2xl border border-rose-100 bg-white p-5 shadow-sm transition hover:shadow-md"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-semibold text-slate-900">{m.name}</p>
                        <p className="text-sm text-slate-600">{m.title}</p>
                      </div>
                      <span className="shrink-0 rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-800">
                        {Math.round(m.match_score * 100)}% fit
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{m.bio}</p>
                    <p className="mt-2 text-xs text-orchid-700">{m.match_reason}</p>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {m.expertise.map((x) => (
                        <span key={x} className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                          {x}
                        </span>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            </section>

            <section>
              <h2 className="font-display text-xl font-semibold text-rose-950">Job opportunities</h2>
              <ul className="mt-4 grid gap-4">
                {result.jobs.map((j) => (
                  <li
                    key={j.id}
                    className="rounded-2xl border border-rose-100 bg-white p-5 shadow-sm transition hover:shadow-md"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <p className="font-semibold text-slate-900">{j.title}</p>
                      <span className="text-sm text-slate-600">
                        {j.company} · {j.location}
                      </span>
                    </div>
                    <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{j.type}</p>
                    <p className="mt-2 text-sm text-slate-600">{j.summary}</p>
                    <p className="mt-2 text-xs text-orchid-700">{j.match_reason}</p>
                  </li>
                ))}
              </ul>
            </section>

            {result.next_steps.length > 0 && (
              <section className="rounded-2xl border border-dashed border-orchid-300 bg-purple-50/60 p-6">
                <h2 className="font-display text-lg font-semibold text-rose-950">Suggested next steps</h2>
                <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-700">
                  {result.next_steps.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ol>
              </section>
            )}
          </div>
        )}
      </main>

      <footer className="mt-16 border-t border-rose-100 py-8 text-center text-xs text-slate-500">
        EmpowerHer · FastAPI · LangGraph · Supabase
      </footer>
    </div>
  );
}
