const isNonEducational = (msg) =>
  msg && msg.toLowerCase().includes('educational');

export default function ErrorDisplay({ error, isDarkTheme }) {
  const notEducational = isNonEducational(error);

  return (
    <div className={`font-inter transition-colors duration-300 ${isDarkTheme ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md px-6">
          <div className="text-6xl mb-4">{notEducational ? '🎓' : '⚠️'}</div>
          <h2 className={`text-2xl font-bold mb-2 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            {notEducational ? 'Not an Educational Video' : 'Error Loading Course'}
          </h2>
          <p className={`mb-2 ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>
            {notEducational
              ? 'LearnTube is designed for academic learning only.'
              : error}
          </p>
          {notEducational && (
            <p className={`mb-6 text-sm ${isDarkTheme ? 'text-gray-400' : 'text-gray-500'}`}>
              Please paste a YouTube link to a lecture, tutorial, course, or educational documentary.
            </p>
          )}
          <button
            onClick={() => window.history.back()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
} 