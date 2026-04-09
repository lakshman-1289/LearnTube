'use client';

import { useState } from 'react';
import Card from "@/components/ui/Card";

export default function QuizSection({ quiz, index, isDarkTheme }) {
  const [selected, setSelected] = useState(null);
  const [revealed, setRevealed] = useState(false);

  const handleReveal = () => setRevealed(r => !r);

  return (
    <Card isDarkTheme={isDarkTheme} className="p-6">
      <h3 className={`text-base font-bold mb-3 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
        Question {index + 1}
      </h3>
      <p className={`mb-4 ${isDarkTheme ? 'text-gray-200' : 'text-gray-800'}`}>
        {quiz.question}
      </p>

      {quiz.type === "multiple_choice" && quiz.options && (
        <div className="space-y-2 mb-4">
          {quiz.options.map((option, i) => {
            const isCorrect = i === quiz.correctAnswer;
            const isSelected = selected === i;
            let stateClass = isDarkTheme
              ? 'border-gray-600 text-gray-300 hover:border-blue-400'
              : 'border-gray-200 text-gray-700 hover:border-blue-400';

            if (revealed) {
              if (isCorrect) stateClass = 'border-green-500 bg-green-50 text-green-800 dark:bg-green-900/30 dark:text-green-300';
              else if (isSelected) stateClass = 'border-red-400 bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300';
            } else if (isSelected) {
              stateClass = isDarkTheme
                ? 'border-blue-400 bg-blue-900/30 text-blue-200'
                : 'border-blue-500 bg-blue-50 text-blue-800';
            }

            return (
              <label
                key={i}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${stateClass}`}
              >
                <input
                  type="radio"
                  name={`quiz-${quiz.id}`}
                  checked={isSelected}
                  onChange={() => !revealed && setSelected(i)}
                  className="accent-blue-500"
                />
                <span className="text-sm">{option}</span>
              </label>
            );
          })}
        </div>
      )}

      <button
        onClick={handleReveal}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
      >
        {revealed ? 'Hide Answer' : 'Show Answer'}
      </button>

      {revealed && (
        <div className={`mt-4 p-4 rounded-lg border ${
          isDarkTheme ? 'bg-green-900/20 border-green-700' : 'bg-green-50 border-green-200'
        }`}>
          <p className={`font-semibold text-sm mb-1 ${isDarkTheme ? 'text-green-300' : 'text-green-700'}`}>
            Correct Answer: {quiz.answer}
          </p>
          {quiz.explanation && (
            <p className={`text-sm mt-2 ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>
              {quiz.explanation}
            </p>
          )}
        </div>
      )}
    </Card>
  );
}
