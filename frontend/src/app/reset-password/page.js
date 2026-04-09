'use client';

import { useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!token) {
      setIsError(true);
      setMessage('Invalid or missing reset token.');
      return;
    }
    if (password.length < 6) {
      setIsError(true);
      setMessage('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirm) {
      setIsError(true);
      setMessage('Passwords do not match.');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setIsError(true);
        setMessage(data.message || 'Something went wrong.');
      } else {
        setIsError(false);
        setMessage('Password reset successful! Redirecting to login...');
        setTimeout(() => router.push('/login'), 2000);
      }
    } catch {
      setIsError(true);
      setMessage('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] flex items-center justify-center p-4">
      <div className="bg-[#161b22] text-white rounded-lg shadow-lg w-full max-w-md p-8">
        <h2 className="text-2xl font-semibold text-center mb-6">Reset Your Password</h2>

        {!token ? (
          <p className="text-red-400 text-center">
            Invalid reset link. Please request a new one from{' '}
            <a href="/forgot-password" className="text-blue-400 underline">Forgot Password</a>.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-gray-300">New Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full p-3 bg-[#0d1117] border border-[#30363d] text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
                placeholder="Min. 6 characters"
                required
                minLength={6}
              />
            </div>
            <div>
              <label className="text-sm text-gray-300">Confirm Password</label>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="mt-1 w-full p-3 bg-[#0d1117] border border-[#30363d] text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600"
                placeholder="Repeat password"
                required
              />
            </div>

            {message && (
              <p className={`text-sm text-center ${isError ? 'text-red-400' : 'text-green-400'}`}>
                {message}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 rounded-md transition duration-300"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-white">Loading...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
