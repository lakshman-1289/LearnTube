'use client';
import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import Link from 'next/link';

function extractVideoId(url) {
  const m = url?.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/);
  return m ? m[1] : url;
}

/* ── Score ring ── */
function ScoreRing({ score, passed }) {
  const r = 54;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <svg width="140" height="140" className="rotate-[-90deg]">
      <circle cx="70" cy="70" r={r} fill="none" stroke="#e5e7eb" strokeWidth="10" />
      <circle
        cx="70" cy="70" r={r} fill="none"
        stroke={passed ? '#22c55e' : '#ef4444'}
        strokeWidth="10"
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        style={{ transition: 'stroke-dasharray 1s ease' }}
      />
      <text x="70" y="70" textAnchor="middle" dominantBaseline="central"
        className="rotate-90" style={{ transform: 'rotate(90deg)', transformOrigin: '70px 70px' }}
        fill={passed ? '#16a34a' : '#dc2626'} fontSize="22" fontWeight="bold">
        {score}%
      </text>
    </svg>
  );
}

export default function ExamPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();
  const videoUrl = searchParams.get('url');
  const videoId = extractVideoId(videoUrl);

  const [phase, setPhase] = useState('loading'); // loading | ready | submitting | result | error
  const [examData, setExamData] = useState(null);  // {course_title, questions}
  const [answers, setAnswers] = useState({});       // {questionId: selectedIndex}
  const [current, setCurrent] = useState(0);
  const [result, setResult] = useState(null);
  const [certLoading, setCertLoading] = useState(false);
  const [cert, setCert] = useState(null);
  const [error, setError] = useState('');
  const [prevResult, setPrevResult] = useState(null);

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status, router]);

  useEffect(() => {
    if (status !== 'authenticated' || !videoId) return;
    Promise.all([
      fetch(`/api/exam/questions?videoId=${videoId}`).then(r => r.json()),
      fetch(`/api/exam/result?videoId=${videoId}`).then(r => r.json()),
    ]).then(([qData, rData]) => {
      if (qData.error) { setError(qData.error); setPhase('error'); return; }
      setExamData(qData);
      if (rData.exists) setPrevResult(rData);
      setPhase('ready');
    }).catch(() => { setError('Failed to load exam'); setPhase('error'); });
  }, [status, videoId]);

  const selectAnswer = (qId, idx) => setAnswers(prev => ({ ...prev, [qId]: idx }));

  const allAnswered = examData?.questions?.every(q => answers[q.id] !== undefined);

  const handleSubmit = async () => {
    setPhase('submitting');
    const payload = {
      video_id: videoId,
      answers: Object.entries(answers).map(([quiz_id, selected_answer]) => ({
        quiz_id: Number(quiz_id),
        selected_answer: Number(selected_answer),
      })),
    };
    try {
      const res = await fetch('/api/exam/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Submission failed');
      setResult(data);
      setPhase('result');
    } catch (e) {
      setError(e.message);
      setPhase('error');
    }
  };

  const handleGetCertificate = async () => {
    setCertLoading(true);
    try {
      const res = await fetch('/api/exam/generate-certificate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setCert(data);
      router.push(`/certificate/${data.certificate_id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setCertLoading(false);
    }
  };

  if (status === 'loading' || phase === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-500">Loading exam...</p>
        </div>
      </div>
    );
  }

  if (phase === 'error') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-5xl mb-4">❌</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Something went wrong</h2>
          <p className="text-gray-500 mb-6">{error}</p>
          <Link href="/" className="bg-blue-600 text-white px-6 py-2 rounded-lg">Go Home</Link>
        </div>
      </div>
    );
  }

  const q = examData?.questions?.[current];
  const total = examData?.questions?.length || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <Link href="/" className="text-xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          LearnTube
        </Link>
        <div className="flex items-center gap-4">
          {videoUrl && (
            <Link href={`/learning?url=${encodeURIComponent(videoUrl)}`} className="text-sm text-gray-500 hover:text-gray-800 transition">
              ← Back to Course
            </Link>
          )}
          <span className="text-sm font-semibold text-gray-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
            Final Exam
          </span>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-10">

        {/* Course title */}
        <div className="text-center mb-8">
          <p className="text-sm text-gray-500 mb-1">Course Assessment</p>
          <h1 className="text-2xl font-bold text-gray-900">{examData?.course_title}</h1>
          <p className="text-sm text-gray-500 mt-2">{total} questions · Pass with 70% or more</p>
        </div>

        {/* Previous result banner */}
        {prevResult && phase === 'ready' && (
          <div className={`mb-6 p-4 rounded-xl border text-sm font-medium ${prevResult.passed ? 'bg-green-50 border-green-200 text-green-700' : 'bg-yellow-50 border-yellow-200 text-yellow-700'}`}>
            {prevResult.passed
              ? `✅ You already passed this exam with ${prevResult.score}%. You can retake it or get your certificate.`
              : `⚠️ Your previous attempt: ${prevResult.score}%. You need 70% to pass. Try again!`}
          </div>
        )}

        {/* ── TAKING PHASE ── */}
        {phase === 'ready' && q && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            {/* Progress bar */}
            <div className="h-1.5 bg-gray-100">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                style={{ width: `${((current + 1) / total) * 100}%` }}
              />
            </div>

            <div className="p-8">
              {/* Question header */}
              <div className="flex items-center justify-between mb-6">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
                  {q.lesson_title}
                </span>
                <span className="text-sm text-gray-400">{current + 1} / {total}</span>
              </div>

              {/* Question */}
              <h2 className="text-lg font-bold text-gray-900 mb-6 leading-snug">{q.question}</h2>

              {/* Options */}
              <div className="space-y-3 mb-8">
                {q.options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => selectAnswer(q.id, i)}
                    className={`w-full text-left px-5 py-3.5 rounded-xl border text-sm font-medium transition-all ${
                      answers[q.id] === i
                        ? 'bg-blue-600 border-blue-600 text-white shadow-md'
                        : 'bg-white border-gray-200 text-gray-700 hover:border-blue-300 hover:bg-blue-50'
                    }`}
                  >
                    <span className={`inline-flex w-6 h-6 rounded-full items-center justify-center text-xs font-bold mr-3 ${
                      answers[q.id] === i ? 'bg-white/20' : 'bg-gray-100'
                    }`}>
                      {['A','B','C','D'][i]}
                    </span>
                    {opt}
                  </button>
                ))}
              </div>

              {/* Nav buttons */}
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setCurrent(c => Math.max(0, c - 1))}
                  disabled={current === 0}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-30 transition"
                >
                  ← Previous
                </button>

                {/* Question dots */}
                <div className="flex gap-1.5 flex-wrap justify-center max-w-xs">
                  {examData.questions.map((qq, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrent(i)}
                      className={`w-6 h-6 rounded-full text-xs font-bold transition ${
                        i === current ? 'bg-blue-600 text-white' :
                        answers[qq.id] !== undefined ? 'bg-green-500 text-white' :
                        'bg-gray-200 text-gray-600 hover:bg-gray-300'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>

                {current < total - 1 ? (
                  <button
                    onClick={() => setCurrent(c => c + 1)}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-blue-600 hover:text-blue-800 transition"
                  >
                    Next →
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    disabled={!allAnswered}
                    className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-bold rounded-xl disabled:opacity-40 disabled:cursor-not-allowed transition shadow"
                  >
                    Submit Exam
                  </button>
                )}
              </div>

              {/* Answer progress */}
              <p className="text-center text-xs text-gray-400 mt-4">
                {Object.keys(answers).length} / {total} answered
                {!allAnswered && current === total - 1 && (
                  <span className="text-yellow-600"> · Answer all questions to submit</span>
                )}
              </p>
            </div>
          </div>
        )}

        {/* ── SUBMITTING ── */}
        {phase === 'submitting' && (
          <div className="bg-white rounded-2xl border border-gray-200 p-16 text-center">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Grading your exam...</p>
          </div>
        )}

        {/* ── RESULT ── */}
        {phase === 'result' && result && (
          <div className="space-y-6">
            {/* Score card */}
            <div className={`bg-white rounded-2xl border p-8 text-center shadow-sm ${result.passed ? 'border-green-200' : 'border-red-200'}`}>
              <div className="flex justify-center mb-4">
                <ScoreRing score={result.score} passed={result.passed} />
              </div>
              <h2 className={`text-2xl font-extrabold mb-1 ${result.passed ? 'text-green-600' : 'text-red-600'}`}>
                {result.passed ? '🎉 Congratulations! You Passed!' : '😔 Not Quite There'}
              </h2>
              <p className="text-gray-500 mb-6">
                {result.correct_count} / {result.total_questions} correct ·{' '}
                {result.passed ? `You scored above the 70% passing mark.` : `You need 70% to pass. Keep studying!`}
              </p>

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                {result.passed && (
                  <button
                    onClick={handleGetCertificate}
                    disabled={certLoading}
                    className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold px-8 py-3 rounded-xl shadow-lg transition disabled:opacity-50"
                  >
                    {certLoading ? (
                      <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Generating...</>
                    ) : (
                      <><span>🏆</span> Get My Certificate</>
                    )}
                  </button>
                )}
                <button
                  onClick={() => { setPhase('ready'); setAnswers({}); setCurrent(0); }}
                  className="inline-flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 font-semibold px-6 py-3 rounded-xl hover:bg-gray-50 transition"
                >
                  🔄 Retake Exam
                </button>
                {videoUrl && (
                  <Link
                    href={`/learning?url=${encodeURIComponent(videoUrl)}`}
                    className="inline-flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 font-semibold px-6 py-3 rounded-xl hover:bg-gray-50 transition"
                  >
                    ← Back to Course
                  </Link>
                )}
              </div>
              {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
            </div>

            {/* Per-question review */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="font-bold text-gray-800">Answer Review</h3>
              </div>
              <div className="divide-y divide-gray-100">
                {result.results.map((r, i) => {
                  const q = examData.questions.find(qq => qq.id === r.quiz_id);
                  return (
                    <div key={r.quiz_id} className="p-5">
                      <div className="flex items-start gap-3">
                        <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${r.correct ? 'bg-green-500' : 'bg-red-500'}`}>
                          {r.correct
                            ? <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                            : <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" /></svg>
                          }
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-gray-800 mb-2">
                            Q{i + 1}. {q?.question}
                          </p>
                          <div className="space-y-1.5">
                            {q?.options.map((opt, oi) => (
                              <div key={oi} className={`text-xs px-3 py-2 rounded-lg ${
                                oi === r.correct_answer ? 'bg-green-100 text-green-700 font-semibold' :
                                oi === r.selected_answer && !r.correct ? 'bg-red-100 text-red-700' :
                                'text-gray-500'
                              }`}>
                                {['A','B','C','D'][oi]}. {opt}
                                {oi === r.correct_answer && ' ✓'}
                                {oi === r.selected_answer && !r.correct && ' ✗'}
                              </div>
                            ))}
                          </div>
                          {r.explanation && (
                            <p className="text-xs text-gray-500 mt-2 italic">💡 {r.explanation}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
