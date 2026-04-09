'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';

export default function HomePage() {
  const [url, setUrl] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [imgError, setImgError] = useState(false);
  const router = useRouter();
  const { data: session, status } = useSession();
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url) return;
    const learningUrl = `/learning?url=${encodeURIComponent(url)}`;
    if (!session) {
      // Require login first; redirect back to learning after
      router.push(`/login?callbackUrl=${encodeURIComponent(learningUrl)}`);
    } else {
      router.push(learningUrl);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white shadow-md">
        <div className="text-xl font-bold text-blue-600">LearnTube</div>

        <div className="flex items-center gap-4">
          {status === 'loading' ? null : session ? (
            /* Logged-in state: avatar dropdown */
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(prev => !prev)}
                className="flex items-center gap-2 rounded-full border border-gray-200 px-3 py-1 hover:bg-gray-50 transition"
              >
                {session.user.image && !imgError ? (
                  <img
                    src={session.user.image}
                    onError={() => setImgError(true)}
                    alt="avatar"
                    className="w-7 h-7 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                    {(session.user.name?.[0] || session.user.email?.[0] || 'U').toUpperCase()}
                  </div>
                )}
                <span className="text-sm font-medium text-gray-700 hidden sm:inline">
                  {session.user.name || session.user.email?.split('@')[0]}
                </span>
                <svg className={`w-3 h-3 text-gray-500 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown — click-toggled */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-1 w-52 bg-white border border-gray-100 rounded-xl shadow-xl z-20 py-1">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-semibold text-gray-800 truncate">
                      {session.user.name || 'User'}
                    </p>
                    <p className="text-xs text-gray-500 truncate">{session.user.email}</p>
                  </div>
                  <Link
                    href="/profile"
                    onClick={() => setIsDropdownOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition"
                  >
                    My Profile
                  </Link>
                  <Link
                    href="/history"
                    onClick={() => setIsDropdownOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition"
                  >
                    Learning History
                  </Link>
                  <div className="border-t border-gray-100 my-1" />
                  <button
                    onClick={() => { setIsDropdownOpen(false); signOut({ callbackUrl: '/' }); }}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 transition"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* Logged-out state */
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm text-gray-700 hover:text-blue-600 font-medium transition"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                className="text-sm bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow px-4 py-10 flex flex-col items-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-center bg-gradient-to-r from-pink-500 to-blue-500 text-transparent bg-clip-text">
          Unlock Knowledge from YouTube videos
        </h1>

        <p className="text-center text-gray-600 mt-4 max-w-2xl">
          Paste a YouTube video link below and LearnTube will extract transcripts, summaries, and generate quizzes to test your understanding.
        </p>

        {/* Converter Card */}
        <div className="bg-white shadow-lg rounded-xl p-6 mt-10 w-full max-w-2xl border">
          <div className="flex items-center gap-2 text-gray-800 text-lg font-semibold mb-4">
            <span>⚙️</span>
            <span>LearnTube</span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">Convert YouTube to Text</h2>
          <p className="text-gray-600 mb-6">
            Enter any YouTube URL to generate the content, quizzes, and mock tests.
          </p>

          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2 text-gray-800 font-semibold text-md">
              <span>⬇️</span>
              <span>Generate Settings</span>
            </div>
            <p className="text-sm text-gray-600 mb-2">Enter a YouTube URL and click generate.</p>

            <label className="block text-sm font-medium text-gray-700 mb-1">YouTube URL</label>
            <input
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <button
            onClick={handleSubmit}
            className="mt-4 w-full bg-red-400 hover:bg-red-500 text-white font-semibold py-2 px-4 rounded-lg transition"
          >
            Generate
          </button>
        </div>
      </main>
    </div>
  );
}
