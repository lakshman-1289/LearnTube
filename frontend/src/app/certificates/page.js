"use client";
import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function CertificatesPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [certs, setCerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === "unauthenticated") { router.push("/login"); return; }
    if (status !== "authenticated") return;
    fetch("/api/exam/my-certificates")
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setCerts(data);
        else if (Array.isArray(data.certificates)) setCerts(data.certificates);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [status]);

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
  };

  const scorePercent = (cert) => {
    if (!cert.total_questions) return 0;
    return Math.round((cert.score / cert.total_questions) * 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-purple-50/30">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span className="font-bold text-gray-900">LearnTube</span>
          </Link>
          <Link href="/history" className="text-sm text-gray-500 hover:text-gray-700 font-medium transition-colors">
            Learning History
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* Title */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Certificates</h1>
          <p className="text-gray-500">Certificates you've earned by completing courses and passing exams.</p>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : certs.length === 0 ? (
          <div className="text-center py-24">
            <div className="w-24 h-24 bg-indigo-50 rounded-3xl flex items-center justify-center mx-auto mb-6">
              <span className="text-5xl">🎓</span>
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">No certificates yet</h3>
            <p className="text-gray-500 mb-6 max-w-sm mx-auto">
              Complete a course and pass the proficiency exam to earn your first certificate.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition-opacity shadow-md"
            >
              Start Learning
            </Link>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {certs.map((cert) => (
              <Link
                key={cert.certificate_id || cert._id}
                href={`/certificate/${cert.certificate_id || cert._id}`}
                className="group bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer"
              >
                {/* Top gradient bar */}
                <div className="h-1.5 -mx-6 -mt-6 mb-6 rounded-t-2xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

                {/* Medal */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-yellow-300 to-amber-400 flex items-center justify-center shadow-md shadow-amber-100">
                    <span className="text-2xl">🏆</span>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-indigo-600">{scorePercent(cert)}%</div>
                    <div className="text-xs text-gray-400">{cert.score}/{cert.total_questions} correct</div>
                  </div>
                </div>

                {/* Course title */}
                <h3 className="font-bold text-gray-900 text-base leading-snug mb-1 group-hover:text-indigo-700 transition-colors line-clamp-2">
                  {cert.course_title}
                </h3>
                <p className="text-sm text-gray-500 mb-4">{cert.user_name}</p>

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                  <span className="text-xs text-gray-400">{formatDate(cert.issued_at)}</span>
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg group-hover:bg-indigo-100 transition-colors">
                    View →
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
