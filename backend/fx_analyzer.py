import yfinance as yf
import pandas as pd
import pandas_ta as ta
from transformers import pipeline
from newsapi import NewsApiClient
import matplotlib.pyplot as plt
import io
import base64
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class FXAnalyzer:
    def __init__(self):
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.news_client = NewsApiClient(api_key=self.news_api_key) if self.news_api_key else None
        self.sentiment_analyzer = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _initialize_sentiment_analyzer(self):
        """Initialize the sentiment analyzer lazily"""
        if self.sentiment_analyzer is None:
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                                 model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            except Exception as e:
                logger.warning(f"Failed to load advanced sentiment model, using default: {e}")
                self.sentiment_analyzer = pipeline("sentiment-analysis")
        return self.sentiment_analyzer

    async def fetch_chart_data(self, pair: str, interval: str, period: str = "7d") -> pd.DataFrame:
        """Fetch forex chart data using yfinance"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                self.executor, 
                lambda: yf.download(pair, interval=interval, period=period, progress=False)
            )
            
            if data.empty:
                raise ValueError(f"No data found for pair {pair}")
                
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in data.columns:
                    logger.warning(f"Column {col} not found in data")
                    
            return data
        except Exception as e:
            logger.error(f"Error fetching chart data: {e}")
            raise

    def apply_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply technical indicators using pandas-ta"""
        try:
            df_copy = df.copy()
            
            # RSI
            df_copy['RSI'] = ta.rsi(df_copy['Close'], length=14)
            
            # MACD
            macd_data = ta.macd(df_copy['Close'])
            if macd_data is not None and not macd_data.empty:
                df_copy['MACD'] = macd_data.iloc[:, 0]  # MACD line
                df_copy['MACD_signal'] = macd_data.iloc[:, 1]  # Signal line
                df_copy['MACD_histogram'] = macd_data.iloc[:, 2]  # Histogram
            else:
                df_copy['MACD'] = 0
                df_copy['MACD_signal'] = 0
                df_copy['MACD_histogram'] = 0
            
            # Moving Averages
            df_copy['MA50'] = ta.sma(df_copy['Close'], length=50)
            df_copy['MA200'] = ta.sma(df_copy['Close'], length=200)
            
            # Bollinger Bands
            bb_data = ta.bbands(df_copy['Close'])
            if bb_data is not None and not bb_data.empty:
                df_copy['BB_upper'] = bb_data.iloc[:, 0]
                df_copy['BB_middle'] = bb_data.iloc[:, 1]
                df_copy['BB_lower'] = bb_data.iloc[:, 2]
            
            return df_copy
            
        except Exception as e:
            logger.error(f"Error applying technical indicators: {e}")
            return df

    def generate_trade_signal(self, df: pd.DataFrame) -> Tuple[str, float, Dict]:
        """Generate trading signal based on technical analysis"""
        try:
            if df.empty:
                return "HOLD", 0.3, {"reason": "No data available"}
                
            latest = df.iloc[-1]
            signals = []
            reasons = []
            
            # RSI Signal
            rsi = latest.get('RSI', 50)
            if pd.notna(rsi):
                if rsi < 30:
                    signals.append(('BUY', 0.3, 'RSI oversold'))
                elif rsi > 70:
                    signals.append(('SELL', 0.3, 'RSI overbought'))
            
            # MACD Signal
            macd = latest.get('MACD', 0)
            macd_signal = latest.get('MACD_signal', 0)
            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal and macd > 0:
                    signals.append(('BUY', 0.2, 'MACD bullish crossover'))
                elif macd < macd_signal and macd < 0:
                    signals.append(('SELL', 0.2, 'MACD bearish crossover'))
            
            # Moving Average Signal
            close = latest.get('Close', 0)
            ma50 = latest.get('MA50')
            ma200 = latest.get('MA200')
            
            if pd.notna(ma50) and pd.notna(ma200) and close > 0:
                if close > ma50 > ma200:
                    signals.append(('BUY', 0.2, 'Price above MAs'))
                elif close < ma50 < ma200:
                    signals.append(('SELL', 0.2, 'Price below MAs'))
            
            # Combine signals
            buy_signals = [s for s in signals if s[0] == 'BUY']
            sell_signals = [s for s in signals if s[0] == 'SELL']
            
            if len(buy_signals) > len(sell_signals):
                confidence = min(0.8, sum(s[1] for s in buy_signals))
                reasons = [s[2] for s in buy_signals]
                return "BUY", confidence, {"reasons": reasons, "rsi": rsi, "macd": macd}
            elif len(sell_signals) > len(buy_signals):
                confidence = min(0.8, sum(s[1] for s in sell_signals))
                reasons = [s[2] for s in sell_signals]
                return "SELL", confidence, {"reasons": reasons, "rsi": rsi, "macd": macd}
            else:
                return "HOLD", 0.4, {"reasons": ["Mixed signals"], "rsi": rsi, "macd": macd}
                
        except Exception as e:
            logger.error(f"Error generating trade signal: {e}")
            return "HOLD", 0.3, {"reason": f"Error: {str(e)}"}

    async def fetch_news(self, keywords: List[str] = None) -> List[str]:
        """Fetch news articles related to forex keywords"""
        if not self.news_client:
            logger.warning("News API client not initialized")
            return []
            
        if keywords is None:
            keywords = ["EURUSD", "ECB", "Federal Reserve", "interest rates", "forex"]
            
        headlines = []
        try:
            loop = asyncio.get_event_loop()
            
            for keyword in keywords[:3]:  # Limit to 3 keywords to avoid API limits
                try:
                    articles = await loop.run_in_executor(
                        self.executor,
                        lambda k=keyword: self.news_client.get_everything(
                            q=k, 
                            language='en', 
                            sort_by='publishedAt', 
                            page_size=5,
                            from_param=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                        )
                    )
                    
                    for article in articles.get('articles', [])[:3]:  # Limit articles per keyword
                        title = article.get('title', '')
                        description = article.get('description', '')
                        if title and description:
                            headlines.append(f"{title} - {description}")
                        elif title:
                            headlines.append(title)
                            
                except Exception as e:
                    logger.warning(f"Error fetching news for keyword {keyword}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            
        return headlines[:10]  # Limit total headlines

    async def analyze_sentiment(self, texts: List[str]) -> Dict:
        """Analyze sentiment of news texts"""
        if not texts:
            return {"sentiment_score": 0, "positive_count": 0, "negative_count": 0, "neutral_count": 0}
            
        try:
            analyzer = self._initialize_sentiment_analyzer()
            loop = asyncio.get_event_loop()
            
            # Process texts in batches to avoid memory issues
            batch_size = 5
            all_results = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_results = await loop.run_in_executor(
                    self.executor,
                    lambda: analyzer(batch)
                )
                all_results.extend(batch_results)
            
            # Process results
            positive_score = 0
            negative_score = 0
            neutral_score = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for result in all_results:
                label = result.get('label', '').upper()
                score = result.get('score', 0)
                
                if 'POSITIVE' in label or label == 'LABEL_2':
                    positive_score += score
                    positive_count += 1
                elif 'NEGATIVE' in label or label == 'LABEL_0':
                    negative_score += score
                    negative_count += 1
                else:
                    neutral_score += score
                    neutral_count += 1
            
            # Calculate overall sentiment score (-1 to 1)
            total_count = len(all_results)
            if total_count > 0:
                sentiment_score = (positive_score - negative_score) / total_count
            else:
                sentiment_score = 0
                
            return {
                "sentiment_score": sentiment_score,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "total_analyzed": total_count
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment_score": 0, "positive_count": 0, "negative_count": 0, "neutral_count": 0, "error": str(e)}

    def combine_signals(self, tech_signal: str, tech_conf: float, sentiment_data: Dict) -> Tuple[str, float, Dict]:
        """Combine technical and sentiment signals"""
        try:
            sentiment_score = sentiment_data.get('sentiment_score', 0)
            
            # Adjust confidence based on sentiment
            sentiment_weight = 0.3
            tech_weight = 0.7
            
            combined_info = {
                "technical_signal": tech_signal,
                "technical_confidence": tech_conf,
                "sentiment_score": sentiment_score,
                "sentiment_data": sentiment_data
            }
            
            if tech_signal == "BUY":
                if sentiment_score > 0.1:  # Positive sentiment
                    final_conf = min(0.9, tech_weight * tech_conf + sentiment_weight * abs(sentiment_score))
                    return "BUY", final_conf, combined_info
                elif sentiment_score < -0.2:  # Strong negative sentiment
                    return "HOLD", 0.4, combined_info
                else:
                    return tech_signal, tech_conf * 0.8, combined_info
                    
            elif tech_signal == "SELL":
                if sentiment_score < -0.1:  # Negative sentiment
                    final_conf = min(0.9, tech_weight * tech_conf + sentiment_weight * abs(sentiment_score))
                    return "SELL", final_conf, combined_info
                elif sentiment_score > 0.2:  # Strong positive sentiment
                    return "HOLD", 0.4, combined_info
                else:
                    return tech_signal, tech_conf * 0.8, combined_info
            else:
                # HOLD signal
                if abs(sentiment_score) > 0.3:
                    signal = "BUY" if sentiment_score > 0 else "SELL"
                    return signal, 0.5, combined_info
                else:
                    return "HOLD", 0.4, combined_info
                    
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return tech_signal, tech_conf, {"error": str(e)}

    def create_chart(self, df: pd.DataFrame, pair: str) -> str:
        """Create a chart and return as base64 string"""
        try:
            plt.style.use('default')
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), height_ratios=[3, 1, 1])
            
            # Price and moving averages
            ax1.plot(df.index, df['Close'], label='Close Price', linewidth=2, color='blue')
            if 'MA50' in df.columns:
                ax1.plot(df.index, df['MA50'], label='MA50', alpha=0.7, color='orange')
            if 'MA200' in df.columns:
                ax1.plot(df.index, df['MA200'], label='MA200', alpha=0.7, color='red')
            
            ax1.set_title(f'{pair} Price Analysis', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI
            if 'RSI' in df.columns:
                ax2.plot(df.index, df['RSI'], label='RSI', color='purple', linewidth=1.5)
                ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
                ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
                ax2.set_ylabel('RSI')
                ax2.set_ylim(0, 100)
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            
            # MACD
            if 'MACD' in df.columns:
                ax3.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=1.5)
                if 'MACD_signal' in df.columns:
                    ax3.plot(df.index, df['MACD_signal'], label='Signal', color='red', linewidth=1.5)
                if 'MACD_histogram' in df.columns:
                    ax3.bar(df.index, df['MACD_histogram'], label='Histogram', alpha=0.3, color='gray')
                ax3.set_ylabel('MACD')
                ax3.set_xlabel('Date')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return ""

    async def analyze_pair(self, pair: str, interval: str = "1h", period: str = "7d") -> Dict:
        """Main analysis function that combines all components"""
        try:
            # Fetch and analyze chart data
            df = await self.fetch_chart_data(pair, interval, period)
            df_with_indicators = self.apply_technical_indicators(df)
            tech_signal, tech_conf, tech_details = self.generate_trade_signal(df_with_indicators)
            
            # Fetch and analyze news
            news_headlines = await self.fetch_news()
            sentiment_data = await self.analyze_sentiment(news_headlines)
            
            # Combine signals
            final_signal, final_conf, combined_info = self.combine_signals(
                tech_signal, tech_conf, sentiment_data
            )
            
            # Create chart
            chart_base64 = self.create_chart(df_with_indicators, pair)
            
            # Get latest values for display
            latest = df_with_indicators.iloc[-1]
            
            return {
                "pair": pair,
                "timestamp": datetime.now().isoformat(),
                "final_signal": final_signal,
                "confidence": round(final_conf, 3),
                "technical_analysis": {
                    "signal": tech_signal,
                    "confidence": round(tech_conf, 3),
                    "details": tech_details,
                    "indicators": {
                        "rsi": round(latest.get('RSI', 0), 2) if pd.notna(latest.get('RSI')) else 0,
                        "macd": round(latest.get('MACD', 0), 4) if pd.notna(latest.get('MACD')) else 0,
                        "close_price": round(latest.get('Close', 0), 5),
                        "ma50": round(latest.get('MA50', 0), 5) if pd.notna(latest.get('MA50')) else 0,
                        "ma200": round(latest.get('MA200', 0), 5) if pd.notna(latest.get('MA200')) else 0
                    }
                },
                "sentiment_analysis": sentiment_data,
                "news_headlines": news_headlines[:5],  # Limit to 5 for response size
                "chart": chart_base64,
                "data_points": len(df_with_indicators),
                "period": period,
                "interval": interval
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_pair: {e}")
            return {
                "pair": pair,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "final_signal": "HOLD",
                "confidence": 0.0
            }