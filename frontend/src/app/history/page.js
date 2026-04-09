'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

function formatDate(dateStr) {
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function progressPercent(completed, total) {
  if (!total) return 0;
  return Math.round((completed / total) * 100);
}

export default function HistoryPage() {
  const { status } = useSession();
  const router = useRouter();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  const handleDelete = async (id) => {
    setDeletingId(id);
    try {
      await fetch(`/api/learning-history?id=${id}`, { method: 'DELETE' });
      setHistory(prev => prev.filter(item => item._id !== id));
    } catch {
      setError('Failed to delete. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const fetchHistory = () => {
    fetch('/api/learning-history', { cache: 'no-store' })
      .then(r => r.json())
      .then(data => {
        if (data.success) setHistory(data.history);
        else setError(data.error || 'Failed to load history');
      })
      .catch(() => setError('Network error'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (status !== 'authenticated') return;
    fetchHistory();
  }, [status]);

  // Re-fetch when tab regains focus (e.g. user comes back from learning page)
  useEffect(() => {
    if (status !== 'authenticated') return;
    const handleFocus = () => fetchHistory();
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [status]);

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Loading your history…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <nav className="bg-white border-b border-gray-200 shadow-sm px-8 py-4 flex items-center justify-between sticky top-0 z-50">
        <Link href="/" className="text-2xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent select-none">
          LearnTube
        </Link>
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-800 transition-colors">
          ← Back to home
        </Link>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Learning History</h1>
        <p className="text-sm text-gray-500 mb-8">Courses you've explored, ready to resume anytime.</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3 mb-6">
            {error}
          </div>
        )}

        {!error && history.length === 0 && (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">📚</div>
            <h2 className="text-lg font-semibold text-gray-800 mb-2">No courses yet</h2>
            <p className="text-gray-500 text-sm mb-6">Paste a YouTube link on the home page to start learning.</p>
            <Link
              href="/"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
            >
              Start learning
            </Link>
          </div>
        )}

        <div className="space-y-4">
          {history.map((item) => {
            const pct = progressPercent(item.completedLessons, item.totalLessons);
            const resumeUrl = `/learning?url=${encodeURIComponent(item.videoUrl)}`;

            return (
              <div
                key={item._id}
                className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex flex-col gap-3"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h2 className="font-semibold text-gray-900 truncate">{item.courseTitle}</h2>
                    {item.courseSubtitle && (
                      <p className="text-sm text-gray-500 truncate mt-0.5">{item.courseSubtitle}</p>
                    )}
                  </div>
                  <span className="text-xs text-gray-400 whitespace-nowrap shrink-0 mt-1">
                    {formatDate(item.lastAccessedAt)}
                  </span>
                </div>

                {/* Progress bar */}
                <div>
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>{item.completedLessons} / {item.totalLessons} lessons</span>
                    <span>{pct}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full transition-all"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Link
                      href={resumeUrl}
                      className="text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-lg transition-colors"
                    >
                      {pct === 100 ? 'Review' : 'Resume'}
                    </Link>
                    <a
                      href={item.videoUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
                    >
                      Watch on YouTube ↗
                    </a>
                  </div>
                  <button
                    onClick={() => handleDelete(item._id)}
                    disabled={deletingId === item._id}
                    className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Delete from history"
                  >
                    {deletingId === item._id ? (
                      <div className="w-4 h-4 border-2 border-red-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
