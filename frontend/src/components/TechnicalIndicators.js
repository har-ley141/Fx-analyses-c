import React from 'react';

const TechnicalIndicators = ({ data }) => {
  const indicators = data?.technical_analysis?.indicators || {};
  
  const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return Number(num).toFixed(decimals);
  };

  const getRSIStatus = (rsi) => {
    if (rsi > 70) return { status: 'Overbought', color: 'text-red-600' };
    if (rsi < 30) return { status: 'Oversold', color: 'text-green-600' };
    return { status: 'Neutral', color: 'text-gray-600' };
  };

  const getMAStatus = (close, ma50, ma200) => {
    if (close > ma50 && ma50 > ma200) return { status: 'Bullish', color: 'text-green-600' };
    if (close < ma50 && ma50 < ma200) return { status: 'Bearish', color: 'text-red-600' };
    return { status: 'Mixed', color: 'text-yellow-600' };
  };

  const rsiStatus = getRSIStatus(indicators.rsi);
  const maStatus = getMAStatus(indicators.close_price, indicators.ma50, indicators.ma200);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Technical Indicators</h2>
      
      <div className="space-y-4">
        {/* RSI */}
        <div className="border-b border-gray-200 pb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">RSI (14)</span>
            <span className={`text-sm font-semibold ${rsiStatus.color}`}>
              {rsiStatus.status}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-gray-900">
              {formatNumber(indicators.rsi, 1)}
            </span>
            <div className="text-right text-sm text-gray-500">
              <div>Overbought: >70</div>
              <div>Oversold: <30</div>
            </div>
          </div>
          {/* RSI Visual Bar */}
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                indicators.rsi > 70 ? 'bg-red-500' : 
                indicators.rsi < 30 ? 'bg-green-500' : 
                'bg-blue-500'
              }`}
              style={{ width: `${Math.min(indicators.rsi || 0, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* MACD */}
        <div className="border-b border-gray-200 pb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">MACD</span>
            <span className={`text-sm font-semibold ${
              indicators.macd > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {indicators.macd > 0 ? 'Bullish' : 'Bearish'}
            </span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(indicators.macd, 4)}
          </div>
        </div>

        {/* Moving Averages */}
        <div className="border-b border-gray-200 pb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Moving Averages</span>
            <span className={`text-sm font-semibold ${maStatus.color}`}>
              {maStatus.status}
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Current Price:</span>
              <span className="text-sm font-semibold">{formatNumber(indicators.close_price, 5)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">MA50:</span>
              <span className="text-sm font-semibold">{formatNumber(indicators.ma50, 5)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">MA200:</span>
              <span className="text-sm font-semibold">{formatNumber(indicators.ma200, 5)}</span>
            </div>
          </div>
        </div>

        {/* Technical Signal Summary */}
        {data?.technical_analysis && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Technical Signal</span>
              <span className={`text-sm font-semibold ${
                data.technical_analysis.signal === 'BUY' ? 'text-green-600' :
                data.technical_analysis.signal === 'SELL' ? 'text-red-600' :
                'text-yellow-600'
              }`}>
                {data.technical_analysis.signal}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {(data.technical_analysis.confidence * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500 mt-1">
              Confidence Level
            </div>
            
            {/* Reasons */}
            {data.technical_analysis.details?.reasons && (
              <div className="mt-3">
                <div className="text-xs font-medium text-gray-700 mb-1">Analysis Factors:</div>
                <div className="space-y-1">
                  {data.technical_analysis.details.reasons.map((reason, index) => (
                    <div key={index} className="text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded">
                      • {reason}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TechnicalIndicators;