import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TradingChart from './TradingChart';
import TechnicalIndicators from './TechnicalIndicators';
import SentimentAnalysis from './SentimentAnalysis';
import NewsPanel from './NewsPanel';
import SignalDisplay from './SignalDisplay';
import PairSelector from './PairSelector';
import LoadingSpinner from './LoadingSpinner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FXDashboard = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPair, setSelectedPair] = useState('EURUSD=X');
  const [selectedInterval, setSelectedInterval] = useState('1h');
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [lastUpdated, setLastUpdated] = useState(null);

  const intervals = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '30m', label: '30 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' }
  ];

  const periods = [
    { value: '1d', label: '1 Day' },
    { value: '5d', label: '5 Days' },
    { value: '7d', label: '1 Week' },
    { value: '1mo', label: '1 Month' },
    { value: '3mo', label: '3 Months' },
    { value: '6mo', label: '6 Months' },
    { value: '1y', label: '1 Year' }
  ];

  const analyzeForexPair = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API}/fx/analyze`, {
        pair: selectedPair,
        interval: selectedInterval,
        period: selectedPeriod
      });
      
      setAnalysisData(response.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze forex pair');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    analyzeForexPair();
  }, [selectedPair, selectedInterval, selectedPeriod]);

  const handleRefresh = () => {
    analyzeForexPair();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <PairSelector value={selectedPair} onChange={setSelectedPair} />
              
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">Interval:</label>
                <select
                  value={selectedInterval}
                  onChange={(e) => setSelectedInterval(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {intervals.map(interval => (
                    <option key={interval.value} value={interval.value}>
                      {interval.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">Period:</label>
                <select
                  value={selectedPeriod}
                  onChange={(e) => setSelectedPeriod(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {periods.map(period => (
                    <option key={period.value} value={period.value}>
                      {period.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {lastUpdated && (
                <span className="text-sm text-gray-500">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </span>
              )}
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Analyzing...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <LoadingSpinner />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="text-red-600 text-sm">
                ⚠️ {error}
              </div>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisData && !loading && (
          <div className="space-y-6">
            {/* Trading Signal */}
            <SignalDisplay data={analysisData} />

            {/* Charts and Indicators Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Trading Chart */}
              <div className="lg:col-span-2">
                <TradingChart data={analysisData} />
              </div>

              {/* Technical Indicators */}
              <div>
                <TechnicalIndicators data={analysisData} />
              </div>
            </div>

            {/* News and Sentiment Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Sentiment Analysis */}
              <SentimentAnalysis data={analysisData} />

              {/* News Panel */}
              <NewsPanel data={analysisData} />
            </div>
          </div>
        )}

        {/* Initial State */}
        {!analysisData && !loading && !error && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">
              Select a forex pair and click Analyze to get started
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FXDashboard;