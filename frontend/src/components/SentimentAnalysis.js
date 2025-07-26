import React from 'react';

const SentimentAnalysis = ({ data }) => {
  const sentiment = data?.sentiment_analysis || {};
  
  const getSentimentColor = (score) => {
    if (score > 0.1) return 'text-green-600';
    if (score < -0.1) return 'text-red-600';
    return 'text-gray-600';
  };

  const getSentimentLabel = (score) => {
    if (score > 0.3) return 'Very Positive';
    if (score > 0.1) return 'Positive';
    if (score < -0.3) return 'Very Negative';
    if (score < -0.1) return 'Negative';
    return 'Neutral';
  };

  const getSentimentIcon = (score) => {
    if (score > 0.1) return '😊';
    if (score < -0.1) return '😟';
    return '😐';
  };

  const total = (sentiment.positive_count || 0) + (sentiment.negative_count || 0) + (sentiment.neutral_count || 0);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">News Sentiment Analysis</h2>
      
      {total > 0 ? (
        <div className="space-y-4">
          {/* Overall Sentiment Score */}
          <div className="text-center">
            <div className="text-4xl mb-2">
              {getSentimentIcon(sentiment.sentiment_score)}
            </div>
            <div className={`text-2xl font-bold ${getSentimentColor(sentiment.sentiment_score)}`}>
              {getSentimentLabel(sentiment.sentiment_score)}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              Score: {(sentiment.sentiment_score * 100).toFixed(1)}%
            </div>
          </div>

          {/* Sentiment Breakdown */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Positive</span>
              </div>
              <span className="text-sm font-semibold">{sentiment.positive_count || 0}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                <span className="text-sm font-medium">Neutral</span>
              </div>
              <span className="text-sm font-semibold">{sentiment.neutral_count || 0}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-sm font-medium">Negative</span>
              </div>
              <span className="text-sm font-semibold">{sentiment.negative_count || 0}</span>
            </div>
          </div>

          {/* Visual Bar */}
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div className="h-full flex">
              {sentiment.positive_count > 0 && (
                <div 
                  className="bg-green-500"
                  style={{ width: `${(sentiment.positive_count / total) * 100}%` }}
                ></div>
              )}
              {sentiment.neutral_count > 0 && (
                <div 
                  className="bg-gray-400"
                  style={{ width: `${(sentiment.neutral_count / total) * 100}%` }}
                ></div>
              )}
              {sentiment.negative_count > 0 && (
                <div 
                  className="bg-red-500"
                  style={{ width: `${(sentiment.negative_count / total) * 100}%` }}
                ></div>
              )}
            </div>
          </div>

          {/* Statistics */}
          <div className="text-center text-sm text-gray-500">
            Analyzed {sentiment.total_analyzed || 0} news articles
          </div>

          {/* Impact on Trading Signal */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-700 mb-1">Impact on Signal:</div>
            <div className="text-xs text-gray-600">
              {sentiment.sentiment_score > 0.1 
                ? "Positive sentiment supports bullish signals" 
                : sentiment.sentiment_score < -0.1 
                ? "Negative sentiment supports bearish signals" 
                : "Neutral sentiment has minimal impact on signals"}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📰</div>
          <div className="text-sm">No news data available</div>
        </div>
      )}

      {sentiment.error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-4">
          <div className="text-sm text-yellow-800">
            ⚠️ {sentiment.error}
          </div>
        </div>
      )}
    </div>
  );
};

export default SentimentAnalysis;