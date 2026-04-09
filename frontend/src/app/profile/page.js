'use client';

import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function ProfilePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [imgError, setImgError] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  if (!session) return null;

  return (
    <div className="min-h-screen bg-[#0d1117] flex flex-col">
      {/* Top bar */}
      <nav className="flex items-center justify-between px-6 py-4 bg-[#161b22] border-b border-[#30363d]">
        <Link href="/" className="text-xl font-bold text-blue-500">
          LearnTube
        </Link>
        <button
          onClick={() => signOut({ callbackUrl: '/' })}
          className="text-sm text-red-400 hover:text-red-300 transition"
        >
          Sign out
        </button>
      </nav>

      {/* Profile card */}
      <main className="flex-grow flex items-center justify-center p-4">
        <div className="bg-[#161b22] text-white rounded-xl shadow-lg w-full max-w-md p-8 border border-[#30363d]">
          {/* Avatar */}
          <div className="flex flex-col items-center mb-6">
            {session.user.image && !imgError ? (
              <img
                src={session.user.image}
                onError={() => setImgError(true)}
                alt="Profile"
                className="w-24 h-24 rounded-full border-4 border-[#30363d] mb-4 object-cover"
              />
            ) : (
              <div className="w-24 h-24 rounded-full border-4 border-[#30363d] mb-4 bg-blue-600 flex items-center justify-center text-white text-4xl font-bold">
                {(session.user.name?.[0] || session.user.email?.[0] || 'U').toUpperCase()}
              </div>
            )}
            <h1 className="text-2xl font-bold">{session.user.name || 'User'}</h1>
            <p className="text-gray-400 text-sm mt-1">{session.user.email}</p>
            {session.user.role && (
              <span className="mt-2 px-3 py-0.5 text-xs rounded-full bg-blue-900 text-blue-300 capitalize">
                {session.user.role}
              </span>
            )}
          </div>

          {/* Details */}
          <div className="space-y-3 text-sm">
            <div className="flex justify-between border-b border-[#30363d] pb-3">
              <span className="text-gray-400">User ID</span>
              <span className="text-gray-200 font-mono text-xs truncate max-w-[60%] text-right">
                {session.user.id || '—'}
              </span>
            </div>
            <div className="flex justify-between border-b border-[#30363d] pb-3">
              <span className="text-gray-400">Email</span>
              <span className="text-gray-200">{session.user.email}</span>
            </div>
            <div className="flex justify-between pb-3">
              <span className="text-gray-400">Auth provider</span>
              <span className="text-gray-200">
                {session.user.image?.includes('googleusercontent') ? 'Google' : 'Email / Password'}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex flex-col gap-3">
            <Link
              href="/"
              className="w-full text-center bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition text-sm font-medium"
            >
              Back to Home
            </Link>
            <button
              onClick={() => signOut({ callbackUrl: '/' })}
              className="w-full bg-[#21262d] hover:bg-[#30363d] text-red-400 border border-[#30363d] py-2 rounded-md transition text-sm font-medium"
            >
              Sign out
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
