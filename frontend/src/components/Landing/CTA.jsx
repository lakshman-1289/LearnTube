'use client';
import { useEffect } from 'react';
import Link from 'next/link';

export default function CTA() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.15 }
    );
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <section className="py-24 relative overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700" />

      {/* Decorative blobs */}
      <div className="pointer-events-none absolute -top-20 -right-20 w-80 h-80 rounded-full bg-white/10 animate-blob" />
      <div className="pointer-events-none absolute -bottom-16 -left-16 w-64 h-64 rounded-full bg-white/10 animate-blob" style={{ animationDelay: '4s' }} />
      <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-white/5" />

      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center reveal">
        <div className="inline-flex items-center gap-2 bg-white/20 border border-white/30 text-white text-xs font-semibold px-3 py-1.5 rounded-full mb-6">
          🚀 Free to use
        </div>
        <h2 className="text-3xl sm:text-5xl font-extrabold text-white mb-6 leading-tight">
          Start learning smarter<br />
          <span className="text-yellow-300">today — for free</span>
        </h2>
        <p className="text-blue-100 text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
          Join learners who are turning YouTube into their personal university.
          No credit card. No setup. Just paste a link.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/signup"
            className="inline-flex items-center justify-center gap-2 bg-white text-blue-700 font-bold px-8 py-4 rounded-full shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-200 text-base"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Start Learning Now
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 border border-white/30 text-white font-semibold px-8 py-4 rounded-full transition-all duration-200 text-base"
          >
            I already have an account
          </Link>
        </div>

        {/* Trust badges */}
        <div className="mt-12 flex flex-wrap justify-center gap-6 text-blue-200 text-sm">
          {['✓ No credit card required', '✓ Works with any YouTube video', '✓ Progress saved automatically'].map(b => (
            <span key={b} className="font-medium">{b}</span>
          ))}
        </div>
      </div>
    </section>
  );
}
