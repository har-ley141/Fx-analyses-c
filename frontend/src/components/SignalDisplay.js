import React from 'react';

const SignalDisplay = ({ data }) => {
  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'SELL':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'BUY':
        return '📈';
      case 'SELL':
        return '📉';
      default:
        return '⏸️';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'text-green-600';
    if (confidence >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Trading Signal</h2>
      
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Main Signal */}
        <div className="flex items-center gap-4">
          <div className={`px-6 py-3 rounded-lg border-2 font-bold text-lg ${getSignalColor(data.final_signal)}`}>
            <span className="mr-2">{getSignalIcon(data.final_signal)}</span>
            {data.final_signal}
          </div>
          
          <div className="text-center">
            <div className="text-sm text-gray-500">Confidence</div>
            <div className={`text-2xl font-bold ${getConfidenceColor(data.confidence)}`}>
              {(data.confidence * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Pair and Timestamp */}
        <div className="text-right">
          <div className="text-lg font-semibold text-gray-900">{data.pair}</div>
          <div className="text-sm text-gray-500">
            {new Date(data.timestamp).toLocaleString()}
          </div>
          <div className="text-xs text-gray-400">
            {data.data_points} data points • {data.interval} • {data.period}
          </div>
        </div>
      </div>

      {/* Technical Analysis Summary */}
      {data.technical_analysis && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-500">Technical Signal</div>
              <div className={`font-semibold ${getSignalColor(data.technical_analysis.signal)} inline-block px-3 py-1 rounded`}>
                {data.technical_analysis.signal}
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-sm text-gray-500">Sentiment Score</div>
              <div className={`font-semibold ${data.sentiment_analysis?.sentiment_score > 0 ? 'text-green-600' : data.sentiment_analysis?.sentiment_score < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                {data.sentiment_analysis?.sentiment_score ? 
                  (data.sentiment_analysis.sentiment_score > 0 ? '+' : '') + 
                  (data.sentiment_analysis.sentiment_score * 100).toFixed(1) + '%' : 
                  'N/A'
                }
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-sm text-gray-500">Current Price</div>
              <div className="text-lg font-semibold text-gray-900">
                {data.technical_analysis.indicators?.close_price?.toFixed(5) || 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SignalDisplay;