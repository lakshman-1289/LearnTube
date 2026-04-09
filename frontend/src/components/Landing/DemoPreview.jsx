'use client';
import { useRef, useEffect } from 'react';

const mockLessons = [
  { id: 1, title: 'Introduction to AI', done: true },
  { id: 2, title: 'Neural Networks Basics', done: true },
  { id: 3, title: 'Training & Optimization', done: false, active: true },
  { id: 4, title: 'Real-world Applications', done: false },
];

export default function DemoPreview() {
  const cardRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.1 }
    );
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const handleMouseMove = (e) => {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 10;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -10;
    el.style.transform = `perspective(1200px) rotateX(${y}deg) rotateY(${x}deg) scale(1.02)`;
  };
  const handleMouseLeave = () => {
    if (cardRef.current)
      cardRef.current.style.transform = 'perspective(1200px) rotateX(0) rotateY(0) scale(1)';
  };

  return (
    <section className="py-24 bg-gradient-to-b from-gray-50 to-white overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">

        {/* Header */}
        <div className="text-center mb-16 reveal">
          <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-4">
            👁️ Live preview
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-4">
            See what your course <span className="grad-text">looks like</span>
          </h2>
          <p className="text-gray-500 max-w-lg mx-auto">
            A clean, distraction-free learning interface with everything you need.
          </p>
        </div>

        {/* Mock browser */}
        <div
          ref={cardRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="reveal tilt-card max-w-5xl mx-auto rounded-2xl overflow-hidden shadow-2xl border border-gray-200 bg-white"
          style={{ transition: 'transform 0.2s ease' }}
        >
          {/* Browser chrome */}
          <div className="bg-gray-100 px-4 py-3 flex items-center gap-3 border-b border-gray-200">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-yellow-400" />
              <div className="w-3 h-3 rounded-full bg-green-400" />
            </div>
            <div className="flex-1 bg-white rounded-md px-3 py-1 text-xs text-gray-400 border border-gray-200 max-w-sm mx-auto text-center">
              learntube.app/learning?url=...
            </div>
          </div>

          {/* App UI */}
          <div className="flex h-[420px]">

            {/* Content area */}
            <div className="flex-1 p-8 overflow-hidden">
              {/* Lesson title */}
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xl font-bold text-gray-900">Training & Optimization</h3>
                <span className="text-sm font-semibold text-blue-600 bg-blue-50 px-3 py-1 rounded-full">3 / 4</span>
              </div>
              <p className="text-sm text-gray-500 mb-6">Understanding how neural networks learn from data</p>

              {/* Tabs */}
              <div className="flex gap-1 mb-6">
                {['Video Lesson', 'Written Lesson'].map((t, i) => (
                  <button key={t} className={`text-sm px-4 py-1.5 rounded-lg font-medium transition ${i === 1 ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'}`}>{t}</button>
                ))}
              </div>

              {/* Content */}
              <div className="space-y-4">
                <p className="text-sm text-gray-700 leading-relaxed">
                  Training a neural network involves adjusting the weights and biases through a process called <strong>backpropagation</strong>, guided by an optimizer such as Stochastic Gradient Descent (SGD) or Adam.
                </p>
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                  <h4 className="text-sm font-bold text-blue-800 mb-2">Key Concepts</h4>
                  <ul className="space-y-1.5">
                    {['Loss function measures prediction error', 'Gradient descent minimizes loss', 'Learning rate controls step size'].map(pt => (
                      <li key={pt} className="flex items-start gap-2 text-sm text-blue-700">
                        <span className="mt-0.5 w-4 h-4 rounded-full bg-blue-200 flex items-center justify-center shrink-0">
                          <svg className="w-2.5 h-2.5 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                        </span>
                        {pt}
                      </li>
                    ))}
                  </ul>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Proper optimization ensures the model converges to a solution that generalises well to unseen data — the ultimate goal of machine learning.
                </p>
              </div>
            </div>

            {/* Sidebar */}
            <div className="w-64 border-l border-gray-100 bg-gray-50/60 p-5 overflow-hidden">
              {/* Progress */}
              <div className="mb-5">
                <div className="flex justify-between text-xs text-gray-500 mb-1.5">
                  <span className="font-medium">Course Progress</span>
                  <span className="font-bold text-gray-700">50%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full w-1/2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" />
                </div>
              </div>

              {/* Lesson list */}
              <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Lessons</p>
              <div className="space-y-2">
                {mockLessons.map(l => (
                  <div key={l.id} className={`flex items-start gap-2.5 p-2.5 rounded-xl text-xs transition ${l.active ? 'bg-blue-100 border border-blue-200' : 'hover:bg-gray-100'}`}>
                    <div className={`mt-0.5 w-4 h-4 rounded-full border flex items-center justify-center shrink-0 ${
                      l.done ? 'bg-green-500 border-green-500' : l.active ? 'border-blue-400 bg-white' : 'border-gray-300 bg-white'
                    }`}>
                      {l.done && <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                      {l.active && <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />}
                    </div>
                    <span className={`leading-tight ${l.active ? 'text-blue-700 font-semibold' : l.done ? 'text-gray-500 line-through' : 'text-gray-700'}`}>
                      {l.id}. {l.title}
                    </span>
                  </div>
                ))}
              </div>

              {/* Quiz CTA */}
              <div className="mt-5 bg-purple-50 border border-purple-100 rounded-xl p-3 text-center">
                <p className="text-xs font-bold text-purple-700 mb-1.5">Ready to test yourself?</p>
                <div className="bg-purple-600 text-white text-xs font-semibold py-1.5 px-3 rounded-lg">Take Quiz</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
