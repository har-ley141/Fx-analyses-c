#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FX Analyzer API
Tests all backend functionality including API endpoints, FX analysis engine, 
technical indicators, news sentiment analysis, and chart generation.
"""

import asyncio
import requests
import json
import os
import sys
from datetime import datetime
import base64
from typing import Dict, List, Any

# Add backend to path for imports
sys.path.append('/app/backend')

# Test configuration
BACKEND_URL = "https://7167c4a0-d769-46da-b520-d400fbd4594c.preview.emergentagent.com/api"
TEST_PAIRS = ["EURUSD=X", "GBPUSD=X"]
TEST_INTERVALS = ["1h", "4h", "1d"]
TEST_PERIODS = ["7d", "1mo"]

class FXAnalyzerTester:
    def __init__(self):
        self.results = {
            "api_endpoints": {},
            "fx_analysis_engine": {},
            "technical_indicators": {},
            "news_sentiment": {},
            "chart_generation": {},
            "errors": []
        }
        
    def log_result(self, category: str, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if category not in self.results:
            self.results[category] = {}
        self.results[category][test_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {category} - {test_name}: {details}")
        
    def log_error(self, error: str):
        """Log error"""
        self.results["errors"].append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🚨 ERROR: {error}")

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "FX Analyzer API" in data.get("message", ""):
                    self.log_result("api_endpoints", "root_endpoint", True, "API root accessible")
                    return True
                else:
                    self.log_result("api_endpoints", "root_endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_result("api_endpoints", "root_endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("api_endpoints", "root_endpoint", False, f"Exception: {str(e)}")
        return False

    def test_supported_pairs_endpoint(self):
        """Test GET /api/fx/pairs endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/fx/pairs", timeout=10)
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                if len(pairs) >= 6:  # Should have at least 6 pairs
                    required_pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]
                    found_pairs = [p["symbol"] for p in pairs]
                    missing = [p for p in required_pairs if p not in found_pairs]
                    if not missing:
                        self.log_result("api_endpoints", "supported_pairs", True, f"Found {len(pairs)} pairs")
                        return True
                    else:
                        self.log_result("api_endpoints", "supported_pairs", False, f"Missing pairs: {missing}")
                else:
                    self.log_result("api_endpoints", "supported_pairs", False, f"Only {len(pairs)} pairs found")
            else:
                self.log_result("api_endpoints", "supported_pairs", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("api_endpoints", "supported_pairs", False, f"Exception: {str(e)}")
        return False

    def test_fx_analyze_endpoint(self, pair: str = "EURUSD=X", interval: str = "1h", period: str = "7d"):
        """Test POST /api/fx/analyze endpoint"""
        try:
            payload = {
                "pair": pair,
                "interval": interval,
                "period": period
            }
            response = requests.post(f"{BACKEND_URL}/fx/analyze", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["pair", "timestamp", "final_signal", "confidence", 
                                 "technical_analysis", "sentiment_analysis", "chart"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Validate signal
                    signal = data.get("final_signal")
                    confidence = data.get("confidence", 0)
                    
                    if signal in ["BUY", "SELL", "HOLD"] and 0 <= confidence <= 1:
                        self.log_result("api_endpoints", f"fx_analyze_{pair}_{interval}_{period}", True, 
                                      f"Signal: {signal}, Confidence: {confidence:.3f}")
                        return data
                    else:
                        self.log_result("api_endpoints", f"fx_analyze_{pair}_{interval}_{period}", False, 
                                      f"Invalid signal/confidence: {signal}/{confidence}")
                else:
                    self.log_result("api_endpoints", f"fx_analyze_{pair}_{interval}_{period}", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("api_endpoints", f"fx_analyze_{pair}_{interval}_{period}", False, 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
        except Exception as e:
            self.log_result("api_endpoints", f"fx_analyze_{pair}_{interval}_{period}", False, f"Exception: {str(e)}")
        return None

    def test_fx_news_endpoint(self):
        """Test GET /api/fx/news endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/fx/news", timeout=15)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["headlines", "sentiment", "timestamp"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    headlines = data.get("headlines", [])
                    sentiment = data.get("sentiment", {})
                    
                    if isinstance(headlines, list) and isinstance(sentiment, dict):
                        sentiment_score = sentiment.get("sentiment_score", 0)
                        if -1 <= sentiment_score <= 1:
                            self.log_result("api_endpoints", "fx_news", True, 
                                          f"Headlines: {len(headlines)}, Sentiment: {sentiment_score:.3f}")
                            return data
                        else:
                            self.log_result("api_endpoints", "fx_news", False, 
                                          f"Invalid sentiment score: {sentiment_score}")
                    else:
                        self.log_result("api_endpoints", "fx_news", False, "Invalid data types")
                else:
                    self.log_result("api_endpoints", "fx_news", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("api_endpoints", "fx_news", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("api_endpoints", "fx_news", False, f"Exception: {str(e)}")
        return None

    def test_fx_history_endpoint(self):
        """Test GET /api/fx/history endpoint"""
        try:
            # Test without parameters
            response = requests.get(f"{BACKEND_URL}/fx/history", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and "count" in data:
                    results = data.get("results", [])
                    count = data.get("count", 0)
                    self.log_result("api_endpoints", "fx_history", True, 
                                  f"Retrieved {count} historical records")
                    
                    # Test with pair parameter
                    response2 = requests.get(f"{BACKEND_URL}/fx/history?pair=EURUSD=X&limit=5", timeout=10)
                    if response2.status_code == 200:
                        self.log_result("api_endpoints", "fx_history_filtered", True, "Filtered history works")
                        return True
                    else:
                        self.log_result("api_endpoints", "fx_history_filtered", False, 
                                      f"Filtered status: {response2.status_code}")
                else:
                    self.log_result("api_endpoints", "fx_history", False, "Missing results/count fields")
            else:
                self.log_result("api_endpoints", "fx_history", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("api_endpoints", "fx_history", False, f"Exception: {str(e)}")
        return False

    def test_technical_indicators(self, analysis_data: Dict):
        """Test technical indicators from analysis data"""
        try:
            tech_analysis = analysis_data.get("technical_analysis", {})
            indicators = tech_analysis.get("indicators", {})
            
            # Test RSI
            rsi = indicators.get("rsi", 0)
            if 0 <= rsi <= 100:
                self.log_result("technical_indicators", "rsi_calculation", True, f"RSI: {rsi}")
            else:
                self.log_result("technical_indicators", "rsi_calculation", False, f"Invalid RSI: {rsi}")
            
            # Test MACD
            macd = indicators.get("macd", 0)
            if isinstance(macd, (int, float)):
                self.log_result("technical_indicators", "macd_calculation", True, f"MACD: {macd}")
            else:
                self.log_result("technical_indicators", "macd_calculation", False, f"Invalid MACD: {macd}")
            
            # Test Moving Averages
            ma50 = indicators.get("ma50", 0)
            ma200 = indicators.get("ma200", 0)
            close_price = indicators.get("close_price", 0)
            
            if ma50 > 0 and ma200 > 0 and close_price > 0:
                self.log_result("technical_indicators", "moving_averages", True, 
                              f"MA50: {ma50}, MA200: {ma200}, Close: {close_price}")
            else:
                self.log_result("technical_indicators", "moving_averages", False, 
                              f"Invalid MAs - MA50: {ma50}, MA200: {ma200}")
            
            # Test signal generation
            signal = tech_analysis.get("signal")
            confidence = tech_analysis.get("confidence", 0)
            
            if signal in ["BUY", "SELL", "HOLD"] and 0 <= confidence <= 1:
                self.log_result("technical_indicators", "signal_generation", True, 
                              f"Signal: {signal}, Confidence: {confidence}")
                return True
            else:
                self.log_result("technical_indicators", "signal_generation", False, 
                              f"Invalid signal: {signal}/{confidence}")
                
        except Exception as e:
            self.log_result("technical_indicators", "analysis_error", False, f"Exception: {str(e)}")
        return False

    def test_sentiment_analysis(self, analysis_data: Dict):
        """Test sentiment analysis from analysis data"""
        try:
            sentiment_data = analysis_data.get("sentiment_analysis", {})
            
            # Test sentiment score
            sentiment_score = sentiment_data.get("sentiment_score", 0)
            if -1 <= sentiment_score <= 1:
                self.log_result("news_sentiment", "sentiment_score", True, f"Score: {sentiment_score}")
            else:
                self.log_result("news_sentiment", "sentiment_score", False, f"Invalid score: {sentiment_score}")
            
            # Test sentiment counts
            positive_count = sentiment_data.get("positive_count", 0)
            negative_count = sentiment_data.get("negative_count", 0)
            neutral_count = sentiment_data.get("neutral_count", 0)
            total_analyzed = sentiment_data.get("total_analyzed", 0)
            
            if total_analyzed >= 0 and (positive_count + negative_count + neutral_count) <= total_analyzed:
                self.log_result("news_sentiment", "sentiment_counts", True, 
                              f"Total: {total_analyzed}, Pos: {positive_count}, Neg: {negative_count}")
            else:
                self.log_result("news_sentiment", "sentiment_counts", False, 
                              f"Invalid counts - Total: {total_analyzed}")
            
            # Test news headlines
            headlines = analysis_data.get("news_headlines", [])
            if isinstance(headlines, list):
                self.log_result("news_sentiment", "news_headlines", True, f"Headlines: {len(headlines)}")
                return True
            else:
                self.log_result("news_sentiment", "news_headlines", False, "Headlines not a list")
                
        except Exception as e:
            self.log_result("news_sentiment", "analysis_error", False, f"Exception: {str(e)}")
        return False

    def test_chart_generation(self, analysis_data: Dict):
        """Test chart generation from analysis data"""
        try:
            chart_data = analysis_data.get("chart", "")
            
            if chart_data:
                # Test if it's valid base64
                try:
                    decoded = base64.b64decode(chart_data)
                    if len(decoded) > 1000:  # Should be a reasonable size for PNG
                        self.log_result("chart_generation", "base64_chart", True, 
                                      f"Chart size: {len(decoded)} bytes")
                        
                        # Test if it starts with PNG header
                        if decoded.startswith(b'\x89PNG'):
                            self.log_result("chart_generation", "png_format", True, "Valid PNG format")
                            return True
                        else:
                            self.log_result("chart_generation", "png_format", False, "Not PNG format")
                    else:
                        self.log_result("chart_generation", "base64_chart", False, f"Chart too small: {len(decoded)}")
                except Exception as decode_error:
                    self.log_result("chart_generation", "base64_chart", False, f"Invalid base64: {str(decode_error)}")
            else:
                self.log_result("chart_generation", "base64_chart", False, "No chart data")
                
        except Exception as e:
            self.log_result("chart_generation", "analysis_error", False, f"Exception: {str(e)}")
        return False

    def test_fx_analysis_engine(self):
        """Test the complete FX analysis engine"""
        try:
            # Test with different pairs and intervals
            success_count = 0
            total_tests = 0
            
            for pair in TEST_PAIRS[:2]:  # Test first 2 pairs
                for interval in TEST_INTERVALS[:2]:  # Test first 2 intervals
                    total_tests += 1
                    analysis_data = self.test_fx_analyze_endpoint(pair, interval, "7d")
                    if analysis_data:
                        success_count += 1
                        
                        # Test technical indicators
                        self.test_technical_indicators(analysis_data)
                        
                        # Test sentiment analysis
                        self.test_sentiment_analysis(analysis_data)
                        
                        # Test chart generation
                        self.test_chart_generation(analysis_data)
            
            if success_count == total_tests:
                self.log_result("fx_analysis_engine", "complete_analysis", True, 
                              f"All {total_tests} analysis tests passed")
                return True
            else:
                self.log_result("fx_analysis_engine", "complete_analysis", False, 
                              f"Only {success_count}/{total_tests} tests passed")
                
        except Exception as e:
            self.log_result("fx_analysis_engine", "complete_analysis", False, f"Exception: {str(e)}")
        return False

    def test_data_validation(self):
        """Test data validation and error handling"""
        try:
            # Test invalid pair
            invalid_payload = {"pair": "INVALID=X", "interval": "1h", "period": "7d"}
            response = requests.post(f"{BACKEND_URL}/fx/analyze", json=invalid_payload, timeout=15)
            
            if response.status_code in [400, 500]:  # Should handle error gracefully
                self.log_result("fx_analysis_engine", "invalid_pair_handling", True, 
                              f"Handled invalid pair with status {response.status_code}")
            else:
                # If it returns 200, check if it has error handling in response
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data or data.get("final_signal") == "HOLD":
                        self.log_result("fx_analysis_engine", "invalid_pair_handling", True, 
                                      "Handled invalid pair gracefully")
                    else:
                        self.log_result("fx_analysis_engine", "invalid_pair_handling", False, 
                                      "No error handling for invalid pair")
                else:
                    self.log_result("fx_analysis_engine", "invalid_pair_handling", False, 
                                  f"Unexpected status: {response.status_code}")
            
            # Test invalid interval
            invalid_interval = {"pair": "EURUSD=X", "interval": "invalid", "period": "7d"}
            response2 = requests.post(f"{BACKEND_URL}/fx/analyze", json=invalid_interval, timeout=15)
            
            if response2.status_code in [400, 500] or (response2.status_code == 200 and "error" in response2.json()):
                self.log_result("fx_analysis_engine", "invalid_interval_handling", True, "Handled invalid interval")
            else:
                self.log_result("fx_analysis_engine", "invalid_interval_handling", False, "No error handling for invalid interval")
                
        except Exception as e:
            self.log_result("fx_analysis_engine", "data_validation_error", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting FX Analyzer Backend Tests...")
        print("=" * 60)
        
        # Test API endpoints
        print("\n📡 Testing API Endpoints...")
        self.test_api_root()
        self.test_supported_pairs_endpoint()
        self.test_fx_news_endpoint()
        self.test_fx_history_endpoint()
        
        # Test FX Analysis Engine
        print("\n🔍 Testing FX Analysis Engine...")
        self.test_fx_analysis_engine()
        
        # Test data validation
        print("\n✅ Testing Data Validation...")
        self.test_data_validation()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        # Count results
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            if category != "errors":
                for test_name, result in tests.items():
                    total_tests += 1
                    if result["success"]:
                        passed_tests += 1
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
        
        if self.results["errors"]:
            print(f"\n🚨 Errors: {len(self.results['errors'])}")
            for error in self.results["errors"][-3:]:  # Show last 3 errors
                print(f"  - {error['error']}")
        
        return self.results

def main():
    """Main test execution"""
    tester = FXAnalyzerTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to /app/backend_test_results.json")
    
    return results

if __name__ == "__main__":
    main()