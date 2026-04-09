"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function CertificatePage() {
  const { id } = useParams();
  const router = useRouter();
  const [cert, setCert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const certRef = useRef(null);

  useEffect(() => {
    fetch(`/api/exam/certificate/${id}`)
      .then(r => r.json())
      .then(data => {
        if (data.error) setError(data.error);
        else setCert(data);
      })
      .catch(() => setError("Failed to load certificate"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDownload = () => {
    window.print();
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500 font-medium">Loading certificate...</p>
        </div>
      </div>
    );
  }

  if (error || !cert) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="text-center max-w-md px-6">
          <div className="text-6xl mb-4">🔍</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Certificate Not Found</h2>
          <p className="text-gray-500 mb-6">{error || "This certificate does not exist or has been removed."}</p>
          <Link href="/" className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition-colors">
            ← Go Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Print styles */}
      <style>{`
        @media print {
          .no-print { display: none !important; }
          body { background: white !important; }
          .cert-wrapper { box-shadow: none !important; }
        }
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      <div className="min-h-screen bg-gradient-to-br from-slate-100 via-indigo-50 to-purple-50 py-10 px-4">
        {/* Action bar */}
        <div className="no-print max-w-4xl mx-auto mb-6 flex items-center justify-between">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back
          </button>
          <div className="flex items-center gap-3">
            <button
              onClick={handleCopyLink}
              className="flex items-center gap-2 bg-white border border-gray-200 text-gray-700 px-4 py-2 rounded-xl font-medium hover:bg-gray-50 transition-colors shadow-sm"
            >
              {copied ? (
                <>
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-green-600">Copied!</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Share Link
                </>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 py-2 rounded-xl font-semibold hover:opacity-90 transition-opacity shadow-md"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download PDF
            </button>
          </div>
        </div>

        {/* Certificate */}
        <div ref={certRef} className="cert-wrapper max-w-4xl mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden">
          {/* Top accent bar */}
          <div className="h-3 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

          <div className="px-16 py-14" style={{ fontFamily: "'Inter', sans-serif" }}>
            {/* Header */}
            <div className="text-center mb-10">
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  LearnTube
                </span>
              </div>
              <p className="text-sm font-semibold tracking-[0.25em] text-gray-400 uppercase mb-2">Certificate of Completion</p>
              <div className="w-24 h-px bg-gradient-to-r from-transparent via-indigo-300 to-transparent mx-auto" />
            </div>

            {/* Medal */}
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="w-28 h-28 rounded-full bg-gradient-to-br from-yellow-300 via-amber-400 to-orange-400 flex items-center justify-center shadow-lg shadow-amber-200">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-200 to-amber-300 flex items-center justify-center border-4 border-white/50">
                    <span className="text-4xl">🏆</span>
                  </div>
                </div>
                {/* Star decorations */}
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                  <span className="text-xs">⭐</span>
                </div>
              </div>
            </div>

            {/* This certifies */}
            <div className="text-center mb-10">
              <p className="text-gray-500 text-lg mb-2">This is to certify that</p>
              <h1
                className="text-5xl font-bold text-gray-900 mb-4"
                style={{ fontFamily: "'Playfair Display', Georgia, serif", letterSpacing: "-0.02em" }}
              >
                {cert.user_name}
              </h1>
              <p className="text-gray-500 text-lg mb-3">has successfully completed</p>
              <div className="inline-block bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-2xl px-8 py-4 mb-4">
                <h2 className="text-2xl font-bold text-gray-800 leading-tight">{cert.course_title}</h2>
              </div>
              <p className="text-gray-500">
                with a score of{" "}
                <span className="font-bold text-indigo-600 text-xl">
                  {cert.score}/{cert.total_questions}
                </span>
                {" "}({Math.round((cert.score / cert.total_questions) * 100)}%)
              </p>
            </div>

            {/* Divider */}
            <div className="border-t border-dashed border-gray-200 mb-10" />

            {/* Footer info */}
            <div className="flex items-end justify-between">
              {/* Issued date */}
              <div className="text-center">
                <div className="w-40 border-b-2 border-gray-300 mb-2" />
                <p className="text-sm text-gray-500">Date Issued</p>
                <p className="font-semibold text-gray-700">{formatDate(cert.issued_at)}</p>
              </div>

              {/* Stamp */}
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 rounded-full border-4 border-indigo-200 flex items-center justify-center bg-indigo-50">
                  <div className="text-center">
                    <div className="text-indigo-600 font-bold text-xs leading-tight">VERIFIED</div>
                    <div className="text-indigo-400 text-xs">✓</div>
                  </div>
                </div>
              </div>

              {/* Certificate ID */}
              <div className="text-center">
                <div className="w-40 border-b-2 border-gray-300 mb-2" />
                <p className="text-sm text-gray-500">Certificate ID</p>
                <p className="font-mono font-semibold text-gray-700 text-sm">{cert.certificate_id || id}</p>
              </div>
            </div>
          </div>

          {/* Bottom accent bar */}
          <div className="h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />
        </div>

        {/* Verify notice */}
        <div className="no-print max-w-4xl mx-auto mt-4 text-center text-sm text-gray-400">
          This certificate can be verified at:{" "}
          <span className="font-mono text-indigo-500">{typeof window !== "undefined" ? window.location.href : ""}</span>
        </div>

        {/* Go to certificates */}
        <div className="no-print max-w-4xl mx-auto mt-6 text-center">
          <Link href="/certificates" className="text-indigo-600 hover:text-indigo-700 font-medium text-sm inline-flex items-center gap-1">
            View all my certificates →
          </Link>
        </div>
      </div>
    </>
  );
}
