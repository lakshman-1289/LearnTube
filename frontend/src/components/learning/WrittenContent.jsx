import QuizSection from "./QuizSection";

export default function WrittenContent({ selectedLesson, isDarkTheme }) {
  const { introduction, sections = [], conclusion } = selectedLesson?.content || {};

  return (
    <div className={`prose max-w-none ${isDarkTheme ? 'prose-invert' : 'prose-gray'}`}>

      {/* Introduction */}
      {introduction && (
        <div className="mb-8">
          <h2 className={`text-2xl font-bold mb-3 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            Introduction
          </h2>
          <p className={`leading-relaxed text-base ${isDarkTheme ? 'text-gray-300' : 'text-gray-700'}`}>
            {introduction}
          </p>
        </div>
      )}

      {/* Content Sections */}
      {sections.length > 0 ? sections.map((section, idx) => (
        <div key={idx} className="mb-8">
          <h2 className={`text-2xl font-bold mb-4 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            {section.title}
          </h2>

          <ul className="space-y-4 list-none pl-0">
            {(section.points || []).map((point, pIdx) => {
              const subtitle = point.subtitle?.trim();
              const isGeneric =
                !subtitle ||
                subtitle.toLowerCase() === 'detail' ||
                subtitle.toLowerCase() === 'point' ||
                subtitle.toLowerCase() === 'note';

              return (
                <li key={pIdx} className="flex gap-3 items-start">
                  <span className={`mt-[6px] flex-shrink-0 w-2 h-2 rounded-full ${
                    isDarkTheme ? 'bg-blue-400' : 'bg-blue-500'
                  }`} />
                  <div className="flex-1">
                    {!isGeneric && (
                      <p className={`font-semibold mb-1 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
                        {subtitle}
                      </p>
                    )}
                    <p className={`leading-relaxed ${isDarkTheme ? 'text-gray-300' : 'text-gray-700'}`}>
                      {point.content}
                    </p>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )) : !introduction && (
        <p className={`italic text-sm ${isDarkTheme ? 'text-gray-500' : 'text-gray-400'}`}>
          No written content available for this lesson. Switch to the Video tab.
        </p>
      )}

      {/* Conclusion */}
      {conclusion && (
        <div className="mb-8">
          <h2 className={`text-2xl font-bold mb-3 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            Conclusion
          </h2>
          <p className={`leading-relaxed text-base ${isDarkTheme ? 'text-gray-300' : 'text-gray-700'}`}>
            {conclusion}
          </p>
        </div>
      )}

      {/* Quizzes — each manages its own open/close state */}
      {selectedLesson?.quizzes?.length > 0 && (
        <div className="space-y-6 mt-8 not-prose">
          <h2 className={`text-xl font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            Test Yourself
          </h2>
          {selectedLesson.quizzes.map((quiz, index) => (
            <QuizSection
              key={quiz.id}
              quiz={quiz}
              index={index}
              isDarkTheme={isDarkTheme}
            />
          ))}
        </div>
      )}
    </div>
  );
}
