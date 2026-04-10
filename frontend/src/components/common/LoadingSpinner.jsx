export default function LoadingSpinner({ isDarkTheme, message, slowWarning }) {
  return (
    <div className={`font-inter transition-colors duration-300 ${isDarkTheme ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-sm px-6">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className={`text-lg font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-700'}`}>
            {message || 'Loading course content...'}
          </p>

          {slowWarning ? (
            <div className={`mt-4 p-3 rounded-lg text-sm ${isDarkTheme ? 'bg-yellow-900/40 text-yellow-300' : 'bg-yellow-50 text-yellow-700'}`}>
              <p className="font-semibold mb-1">This is a long video — hang tight!</p>
              <p>Course generation for lengthy videos can take up to an hour. Please keep this tab open until it finishes.</p>
            </div>
          ) : (
            <p className={`text-sm mt-2 ${isDarkTheme ? 'text-gray-500' : 'text-gray-400'}`}>
              This may take a few minutes for new videos
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
