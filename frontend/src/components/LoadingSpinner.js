import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p className="mt-4 text-gray-600">Analyzing forex data...</p>
      <p className="text-sm text-gray-500 mt-1">
        Fetching market data, calculating indicators, and analyzing news sentiment
      </p>
    </div>
  );
};

export default LoadingSpinner;