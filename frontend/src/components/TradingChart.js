import React from 'react';

const TradingChart = ({ data }) => {
  if (!data?.chart) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Chart</h2>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
          <div className="text-gray-500">Chart not available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        {data.pair} Technical Analysis
      </h2>
      
      <div className="relative">
        <img
          src={`data:image/png;base64,${data.chart}`}
          alt={`${data.pair} Chart`}
          className="w-full h-auto rounded-lg border border-gray-200"
        />
        
        {/* Chart Overlay Info */}
        <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded px-3 py-2 text-sm">
          <div className="font-semibold">{data.pair}</div>
          <div className="text-gray-600">{data.interval} • {data.period}</div>
        </div>

        {/* Signal Overlay */}
        <div className={`absolute top-2 right-2 px-3 py-2 rounded text-sm font-semibold ${
          data.final_signal === 'BUY' ? 'bg-green-500/90 text-white' :
          data.final_signal === 'SELL' ? 'bg-red-500/90 text-white' :
          'bg-yellow-500/90 text-white'
        }`}>
          {data.final_signal}
        </div>
      </div>

      {/* Chart Legend */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-blue-500"></div>
          <span>Close Price</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-orange-500"></div>
          <span>MA50</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-red-500"></div>
          <span>MA200</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-purple-500"></div>
          <span>RSI</span>
        </div>
      </div>
    </div>
  );
};

export default TradingChart;