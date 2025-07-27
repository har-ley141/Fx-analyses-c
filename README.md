# Fx-analyses-c

## Directory Structure

```
backend/src/fx-analyzer-api/
│
├── main.py             # The FastAPI backend
├── fx_analyzer.py      # Main analysis script (see below)
├── requirements.txt    # Dependencies
└── .render.yaml        # Render configuration
```

## Render Service Example

```yaml
services:
  - type: web
    name: fx-analyzer-api
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port 10000"
    envVars:
      - key: NEWS_API_KEY
        fromEnvVar: NEWS_API_KEY
```

## Usage

- Make sure to set your `NEWS_API_KEY` as an environment variable.
- Run the script:  
  ```bash
  python fx_analyzer.py
  ```

## Python Analysis Script Example

```python
# fx_analyzer.py

import os
import yfinance as yf
import pandas as pd
import finta
from transformers import pipeline
from newsapi import NewsApiClient
import matplotlib.pyplot as plt

# ========== CONFIG ==========
PAIR = "EURUSD=X"
INTERVAL = "1h"
NEWS_KEYWORDS = ["EURUSD", "ECB", "Federal Reserve", "interest rates"]
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Use env variable!
N_CANDLES = 100

# ========== TECHNICAL ANALYSIS ==========
def fetch_chart_data(pair, interval, period="7d"):
    data = yf.download(pair, interval=interval, period=period)
    return data

def apply_technical_indicators(df):
    df["RSI"] = finta.RSI(df["Close"])
    df["MACD"], _, _ = finta.MACD(df["Close"])
    df["MA50"] = finta.SMA(df["Close"], timeperiod=50)
    df["MA200"] = finta.SMA(df["Close"], timeperiod=200)
    return df

def generate_trade_signal(df):
    latest = df.iloc[-1]
    if latest["RSI"] < 30 and latest["MACD"] > 0:
        return "BUY", 0.7
    elif latest["RSI"] > 70 and latest["MACD"] < 0:
        return "SELL", 0.7
    return "HOLD", 0.3

# ========== NEWS SENTIMENT ANALYSIS ==========
def fetch_news():
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY not set in environment variables.")
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    headlines = []
    for kw in NEWS_KEYWORDS:
        articles = newsapi.get_everything(q=kw, language='en', sort_by='publishedAt', page_size=5)
        for article in articles.get('articles', []):
            title = article.get('title', '')
            description = article.get('description') or ''
            headlines.append(f"{title} - {description}".strip())
    return headlines

def analyze_sentiment(texts):
    classifier = pipeline("sentiment-analysis")
    results = classifier(texts)
    scores = {"POSITIVE": 0, "NEGATIVE": 0}
    for result in results:
        label = result["label"].upper()
        if label in scores:
            scores[label] += result["score"]
    sentiment_score = scores["POSITIVE"] - scores["NEGATIVE"]
    return sentiment_score

# ========== MAIN STRATEGY ==========
def combine_signals(tech_signal, tech_conf, sentiment_score):
    if tech_signal == "BUY" and sentiment_score > 0.2:
        return "BUY", (tech_conf + sentiment_score) / 2
    elif tech_signal == "SELL" and sentiment_score < -0.2:
        return "SELL", (tech_conf + abs(sentiment_score)) / 2
    return "HOLD", 0.4

def main():
    print("🔍 Fetching FX chart data...")
    df = fetch_chart_data(PAIR, INTERVAL)
    df = apply_technical_indicators(df)
    tech_signal, tech_conf = generate_trade_signal(df)

    print("📰 Fetching and analyzing news...")
    news = fetch_news()
    sentiment_score = analyze_sentiment(news)

    print(f"📊 Tech Signal: {tech_signal} ({tech_conf:.2f})")
    print(f"🧠 News Sentiment Score: {sentiment_score:.2f}")

    final_signal, confidence = combine_signals(tech_signal, tech_conf, sentiment_score)
    print(f"📈 Final Signal: {final_signal} (Confidence: {confidence:.2f})")

    # Optional: Plot
    df[["Close", "MA50", "MA200"]].plot(title=f"{PAIR} Price & MAs")
    plt.show()

if __name__ == "__main__":
    main()
```

## Requirements

```txt
fastapi
uvicorn
yfinance
pandas
transformers
torch
newsapi-python
finta
```
