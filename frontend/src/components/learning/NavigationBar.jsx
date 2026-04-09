'use client';

import { useState, useRef, useEffect } from 'react';
import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';
import ThemeToggle from '@/components/common/ThemeToggle';

export default function NavigationBar({ isDarkTheme, setIsDarkTheme }) {
  const { data: session } = useSession();
  const [isOpen, setIsOpen] = useState(false);
  const [imgError, setImgError] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <nav className={`flex items-center justify-between px-8 py-4 border-b sticky top-0 z-50 transition-colors duration-300 ${
      isDarkTheme
        ? 'bg-gray-800/90 backdrop-blur-sm border-gray-700 shadow-lg'
        : 'bg-white border-gray-200 shadow-sm'
    }`}>
      {/* Logo */}
      <Link href="/" className="text-2xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent select-none">
        LearnTube
      </Link>

      <div className="flex items-center gap-4">
        <ThemeToggle isDarkTheme={isDarkTheme} setIsDarkTheme={setIsDarkTheme} />

        {session ? (
          /* ── Profile dropdown ── */
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsOpen(prev => !prev)}
              className={`flex items-center gap-2 rounded-full pl-2 pr-3 py-1 border transition-colors ${
                isDarkTheme
                  ? 'border-gray-600 hover:border-gray-400'
                  : 'border-gray-200 hover:border-gray-400'
              }`}
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
              <span className={`text-sm font-medium hidden sm:inline ${isDarkTheme ? 'text-gray-200' : 'text-gray-700'}`}>
                {session.user.name?.split(' ')[0] || session.user.email?.split('@')[0]}
              </span>
              <svg className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''} ${isDarkTheme ? 'text-gray-400' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown — click-toggled */}
            {isOpen && (
              <div className={`absolute right-0 top-full mt-1 w-52 rounded-xl shadow-xl border py-1 z-50 ${
                isDarkTheme ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-100'
              }`}>
                {/* User info */}
                <div className={`px-4 py-3 border-b ${isDarkTheme ? 'border-gray-700' : 'border-gray-100'}`}>
                  <p className={`text-sm font-semibold truncate ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
                    {session.user.name || 'User'}
                  </p>
                  <p className={`text-xs truncate ${isDarkTheme ? 'text-gray-400' : 'text-gray-500'}`}>
                    {session.user.email}
                  </p>
                </div>

                <Link
                  href="/profile"
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center gap-2 px-4 py-2 text-sm transition-colors ${
                    isDarkTheme ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  My Profile
                </Link>

                <Link
                  href="/history"
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center gap-2 px-4 py-2 text-sm transition-colors ${
                    isDarkTheme ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Learning History
                </Link>

                <div className={`border-t my-1 ${isDarkTheme ? 'border-gray-700' : 'border-gray-100'}`} />

                <button
                  onClick={() => { setIsOpen(false); signOut({ callbackUrl: '/' }); }}
                  className={`flex items-center gap-2 w-full px-4 py-2 text-sm text-red-500 hover:text-red-600 transition-colors ${
                    isDarkTheme ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Sign out
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link
            href="/login"
            className="text-sm font-medium px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Sign in
          </Link>
        )}
      </div>
    </nav>
  );
}
