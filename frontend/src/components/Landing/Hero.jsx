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
            AI-Powered Learning Platform
          </div>

          <h1 className="text-4xl sm:text-5xl xl:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
            Transform YouTube<br />
            <span className="grad-text">Videos into</span><br />
            Structured Courses
          </h1>

          <p className="text-lg text-gray-600 mb-8 max-w-lg leading-relaxed">
            Learn smarter with AI-generated lessons, interactive quizzes, and
            real-time progress tracking — all from any YouTube video.
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

          {/* Lesson card */}
          <FloatingCard delay="0s" rotate="-3deg" className="absolute top-8 left-4 w-64">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-800">Lesson 1 of 4</span>
            </div>
            <p className="text-xs font-bold text-gray-700 mb-2">Introduction to Neural Networks</p>
            <div className="space-y-1.5">
              {['What is a neuron?', 'Layers & weights', 'Activation functions'].map(t => (
                <div key={t} className="flex items-center gap-2">
                  <div className="w-3.5 h-3.5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <svg className="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                  </div>
                  <span className="text-xs text-gray-600">{t}</span>
                </div>
              ))}
            </div>
          </FloatingCard>

          {/* Quiz card */}
          <FloatingCard delay="1.5s" rotate="4deg" className="absolute top-16 right-2 w-60">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-800">Quick Quiz</span>
            </div>
            <p className="text-xs text-gray-700 mb-3 font-medium">What does backpropagation do?</p>
            {['Updates weights backward', 'Feeds data forward', 'Normalizes inputs'].map((opt, i) => (
              <div key={opt} className={`text-xs px-3 py-1.5 rounded-lg mb-1.5 ${i === 0 ? 'bg-green-100 text-green-700 font-semibold border border-green-200' : 'bg-gray-50 text-gray-600'}`}>
                {opt}
              </div>
            ))}
          </FloatingCard>

          {/* Progress card */}
          <FloatingCard delay="0.8s" rotate="-2deg" className="absolute bottom-24 left-8 w-56">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-800">Your Progress</span>
            </div>
            <div className="space-y-2">
              {[['Lessons', 75], ['Quizzes', 60], ['Overall', 68]].map(([label, pct]) => (
                <div key={label}>
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{label}</span><span className="font-semibold text-gray-700">{pct}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </FloatingCard>

          {/* AI badge */}
          <FloatingCard delay="2.2s" rotate="3deg" className="absolute bottom-20 right-6 w-48">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <p className="text-xs font-bold text-gray-800">AI Generated</p>
                <p className="text-xs text-gray-500">4 lessons created</p>
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
