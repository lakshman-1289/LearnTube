import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-950 text-gray-400">
      <div className="max-w-7xl mx-auto px-6 py-14 grid grid-cols-1 sm:grid-cols-3 gap-10">

        {/* Brand */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span className="text-white font-extrabold text-lg">LearnTube</span>
          </div>
          <p className="text-sm leading-relaxed">
            AI-powered learning platform that transforms any YouTube video into structured lessons and quizzes.
          </p>
        </div>

        {/* Links */}
        <div>
          <p className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">Platform</p>
          <ul className="space-y-2 text-sm">
            <li><Link href="/" className="hover:text-white transition">Home</Link></li>
            <li><Link href="/login" className="hover:text-white transition">Login</Link></li>
            <li><Link href="/signup" className="hover:text-white transition">Sign Up</Link></li>
            <li><Link href="/history" className="hover:text-white transition">Learning History</Link></li>
            <li><Link href="/profile" className="hover:text-white transition">Profile</Link></li>
          </ul>
        </div>

        {/* Credits */}
        <div>
          <p className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">Built with</p>
          <ul className="space-y-2 text-sm">
            {['Next.js 15', 'Tailwind CSS', 'Groq AI (LLaMA 3.1)', 'FastAPI + Python', 'MongoDB'].map(t => (
              <li key={t} className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                {t}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-gray-800 px-6 py-5">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-gray-600">
          <p>© {new Date().getFullYear()} LearnTube. All rights reserved.</p>
          <p>Made with ❤️ to make learning accessible for everyone.</p>
        </div>
      </div>
    </footer>
  );
}
