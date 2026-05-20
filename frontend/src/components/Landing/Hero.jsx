'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';

/* ── Floating 3D card ── */
function FloatingCard({ delay, rotate, className, children }) {
  return (
    <div
      className={`animate-float glass rounded-2xl shadow-xl border border-white/60 p-4 ${className}`}
      style={{ animationDelay: delay, '--rotate': rotate }}
    >
      {children}
    </div>
  );
}

export default function Hero() {
  const { data: session } = useSession();
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    const dest = `/learning?url=${encodeURIComponent(url.trim())}`;
    if (!session) router.push(`/login?callbackUrl=${encodeURIComponent(dest)}`);
    else router.push(dest);
  };

  return (
    <section className="relative min-h-screen mesh-bg flex items-center overflow-hidden pt-20">

      {/* Background blobs */}
      <div className="pointer-events-none absolute -top-32 -left-32 w-96 h-96 rounded-full bg-blue-200/40 animate-blob" style={{ animationDelay: '0s' }} />
      <div className="pointer-events-none absolute top-1/2 -right-24 w-80 h-80 rounded-full bg-purple-200/40 animate-blob" style={{ animationDelay: '3s' }} />
      <div className="pointer-events-none absolute bottom-0 left-1/3 w-64 h-64 rounded-full bg-pink-200/30 animate-blob" style={{ animationDelay: '6s' }} />

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-16 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center w-full">

        {/* LEFT — Text */}
        <div
          className={`transition-all duration-700 ${visible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}`}
          style={{ transitionDelay: '100ms' }}
        >
          <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            LearnTube AI v2.0 Architecture
          </div>

          <h1 className="text-4xl sm:text-5xl xl:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
          AI-Powered<br />
          <span className="grad-text">Course Generation</span><br />
          Platform
        </h1>

          <p className="text-lg text-gray-600 mb-8 max-w-lg leading-relaxed">
            A production-scale LangGraph orchestration engine combining True RAG, K-Means semantic clustering, and Map-Reduce workflows to synthesize massive YouTube transcripts into validated educational courses.
          </p>

          {/* Inline URL form */}
          <div id="try-it" className="bg-white/80 backdrop-blur border border-gray-200 rounded-2xl p-5 shadow-lg max-w-lg">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Paste a YouTube link to get started</p>
            <form onSubmit={handleGenerate} className="flex gap-2">
              <input
                type="url"
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="flex-1 min-w-0 px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
              />
              <button
                type="submit"
                className="shrink-0 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-5 py-2.5 rounded-xl transition shadow"
              >
                Generate
              </button>
            </form>
          </div>

        </div>

        {/* RIGHT — 3D floating cards */}
        <div
          className={`relative h-[520px] hidden lg:block transition-all duration-700 ${visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-10'}`}
          style={{ transitionDelay: '300ms' }}
        >
          {/* Centre circle glow */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-72 h-72 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 animate-pulse-ring" />
          </div>

          {/* Node Graph Card */}
          <FloatingCard delay="0s" rotate="-3deg" className="absolute top-8 left-4 w-64">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-800">LangGraph DAG</span>
            </div>
            <p className="text-xs font-bold text-gray-700 mb-2">Executing Pipeline Nodes</p>
            <div className="space-y-1.5">
              {[
                { name: 'chunk_transcript', status: 'done', color: 'green' },
                { name: 'semantic_clustering', status: 'done', color: 'green' },
                { name: 'map_reduce_extraction', status: 'running', color: 'blue' },
              ].map(t => (
                <div key={t.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3.5 h-3.5 rounded-full bg-${t.color}-400 flex items-center justify-center shrink-0`}>
                      {t.status === 'done' ? <svg className="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg> : <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />}
                    </div>
                    <span className="text-xs font-mono text-gray-600">{t.name}()</span>
                  </div>
                  <span className={`text-[10px] font-bold text-${t.color}-500 uppercase tracking-wider`}>{t.status}</span>
                </div>
              ))}
            </div>
          </FloatingCard>

          {/* RAG Card */}
          <FloatingCard delay="1.5s" rotate="4deg" className="absolute top-16 right-2 w-64">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-800">FAISS Vector Store</span>
            </div>
            <p className="text-xs text-gray-700 mb-3 font-medium">True RAG Architecture</p>
            {['Embedding: all-MiniLM-L6-v2', 'Index Type: L2 distance', 'Dimensions: 384'].map((opt, i) => (
              <div key={opt} className={`text-[11px] font-mono px-3 py-1.5 rounded-lg mb-1.5 bg-gray-50 text-gray-600 border border-gray-100`}>
                {opt}
              </div>
            ))}
          </FloatingCard>

          {/* Token Progress Card */}
          <FloatingCard delay="0.8s" rotate="-2deg" className="absolute bottom-24 left-8 w-60">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-800">Execution Telemetry</span>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Token Limits (TPM)', pct: 85, val: '5.1k / 6.0k' },
                { label: 'Map-Reduce Batches', pct: 40, val: '2 / 5' },
                { label: 'Queue Workers', pct: 100, val: '1 active' }
              ].map(({label, pct, val}) => (
                <div key={label}>
                  <div className="flex justify-between text-[10px] uppercase tracking-wide text-gray-500 mb-1.5">
                    <span>{label}</span><span className="font-bold text-gray-700">{val}</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </FloatingCard>

          {/* Idempotency badge */}
          <FloatingCard delay="2.2s" rotate="3deg" className="absolute bottom-20 right-6 w-48">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-800">Atomic Locks</p>
                <p className="text-[11px] text-gray-500">Idempotency secured</p>
              </div>
            </div>
          </FloatingCard>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce">
        <span className="text-xs text-gray-400 font-medium">Scroll to explore</span>
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </section>
  );
}
