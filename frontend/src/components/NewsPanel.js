import React, { useState } from 'react';

const NewsPanel = ({ data }) => {
  const [expandedNews, setExpandedNews] = useState(null);
  
  const headlines = data?.news_headlines || [];

  const toggleNewsExpansion = (index) => {
    setExpandedNews(expandedNews === index ? null : index);
  };

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Latest Forex News</h2>
      
      {headlines.length > 0 ? (
        <div className="space-y-3">
          {headlines.map((headline, index) => {
            const isExpanded = expandedNews === index;
            const parts = headline.split(' - ');
            const title = parts[0];
            const description = parts.slice(1).join(' - ');
            
            return (
              <div 
                key={index}
                className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => toggleNewsExpansion(index)}
              >
                <div className="flex justify-between items-start gap-2">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm leading-tight">
                      {title}
                    </div>
                    {description && (
                      <div className="text-xs text-gray-600 mt-1">
                        {isExpanded ? description : truncateText(description, 80)}
                      </div>
                    )}
                  </div>
                  <div className="flex-shrink-0 text-gray-400 text-xs">
                    {isExpanded ? '−' : '+'}
                  </div>
                </div>

                {/* News metadata */}
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>📈 Forex</span>
                    <span>•</span>
                    <span>Recent</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    Click to {isExpanded ? 'collapse' : 'expand'}
                  </div>
                </div>
              </div>
            );
          })}

          {/* News Summary */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-sm font-medium text-blue-900 mb-1">
                News Summary
              </div>
              <div className="text-xs text-blue-700">
                {headlines.length} articles analyzed for sentiment impact on {data?.pair || 'forex pair'}.
                {data?.sentiment_analysis?.sentiment_score && (
                  <span className="ml-1">
                    Overall market sentiment: 
                    <span className={`font-semibold ml-1 ${
                      data.sentiment_analysis.sentiment_score > 0 ? 'text-green-600' : 
                      data.sentiment_analysis.sentiment_score < 0 ? 'text-red-600' : 
                      'text-gray-600'
                    }`}>
                      {data.sentiment_analysis.sentiment_score > 0 ? 'Positive' : 
                       data.sentiment_analysis.sentiment_score < 0 ? 'Negative' : 'Neutral'}
                    </span>
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📰</div>
          <div className="text-gray-500 text-sm">No recent news available</div>
          <div className="text-gray-400 text-xs mt-1">
            News sentiment analysis helps improve signal accuracy
          </div>
        </div>
      )}

      {/* News Source Attribution */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          News powered by NewsAPI • Updates every analysis
        </div>
      </div>
    </div>
  );
};

export default NewsPanel;