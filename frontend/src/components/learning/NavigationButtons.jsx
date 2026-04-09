export default function NavigationButtons({ lessons, selectedLessonId, setSelectedLessonId, isDarkTheme }) {
  const currentIndex = lessons?.findIndex(l => l.id === selectedLessonId) ?? -1;
  const isFirst = currentIndex <= 0;
  const isLast = currentIndex >= (lessons?.length ?? 0) - 1;

  const go = (delta) => {
    const next = lessons?.[currentIndex + delta];
    if (next) setSelectedLessonId(next.id);
  };

  const baseBtn = `flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-colors duration-200`;

  return (
    <div className="flex items-center justify-between mt-2">
      <button
        onClick={() => go(-1)}
        disabled={isFirst}
        className={`${baseBtn} border ${
          isFirst
            ? 'opacity-40 cursor-not-allowed border-gray-200 text-gray-400'
            : isDarkTheme
              ? 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
        }`}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Previous lesson
      </button>

      <button
        onClick={() => go(1)}
        disabled={isLast}
        className={`${baseBtn} ${
          isLast
            ? 'opacity-40 cursor-not-allowed bg-blue-600 text-white'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        Next lesson
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
}
