import React from 'react';
import { SentimentData } from '../types/types';

interface SentimentAnalyzerProps {
  sentiment: SentimentData;
  suggestions: string[];
  role: 'customer' | 'support agent';
}

const SentimentAnalyzer: React.FC<SentimentAnalyzerProps> = ({ 
  sentiment, 
  suggestions, 
  role 
}) => {
  const getSentimentColor = () => {
    switch (sentiment.sentiment) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const normalizedScore = (sentiment.score + 1) / 2;

  return (
    <div className="bg-gray-100 p-4 rounded-lg">
      <h3 className="text-lg font-bold mb-3">Sentiment Analysis</h3>
      
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span>😠 Negative</span>
          <span>😊 Positive</span>
        </div>
        <div className="w-full bg-gray-300 rounded-full h-2.5">
          <div 
            className="bg-blue-600 h-2.5 rounded-full" 
            style={{ width: `${normalizedScore * 100}%` }}
          ></div>
        </div>
        <div className={`mt-2 font-semibold ${getSentimentColor()}`}>
          Sentiment: {sentiment.sentiment.toUpperCase()}
          <span className="ml-2 text-gray-600 font-normal">
            (Score: {sentiment.score.toFixed(2)})
          </span>
        </div>
      </div>

      {role === 'support agent' && suggestions.length > 0 && (
        <div className="mt-4">
          <h4 className="font-bold mb-2">🤝 Improvement Suggestions:</h4>
          <ul className="list-disc list-inside">
            {suggestions.map((suggestion, index) => (
              <li 
                key={index} 
                className="mb-2 text-sm text-blue-800 bg-blue-50 p-2 rounded"
              >
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SentimentAnalyzer;