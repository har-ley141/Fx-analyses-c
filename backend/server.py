from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from fx_analyzer import FXAnalyzer

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="FX Analyzer API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize FX Analyzer
fx_analyzer = FXAnalyzer()

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class FXAnalysisRequest(BaseModel):
    pair: str = "EURUSD=X"
    interval: str = "1h"
    period: str = "7d"

class FXAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pair: str
    timestamp: datetime
    final_signal: str
    confidence: float
    technical_analysis: Dict[str, Any]
    sentiment_analysis: Dict[str, Any]
    news_headlines: List[str]
    chart: str
    data_points: int
    period: str
    interval: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Original routes
@api_router.get("/")
async def root():
    return {"message": "FX Analyzer API - Ready for Trading Analysis"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# FX Analysis routes
@api_router.post("/fx/analyze")
async def analyze_forex_pair(request: FXAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a forex pair with technical and sentiment analysis"""
    try:
        # Perform the analysis
        analysis_result = await fx_analyzer.analyze_pair(
            pair=request.pair,
            interval=request.interval,
            period=request.period
        )
        
        # Create result object for database storage
        result_obj = FXAnalysisResult(
            pair=analysis_result.get("pair", request.pair),
            timestamp=datetime.fromisoformat(analysis_result.get("timestamp", datetime.now().isoformat())),
            final_signal=analysis_result.get("final_signal", "HOLD"),
            confidence=analysis_result.get("confidence", 0.0),
            technical_analysis=analysis_result.get("technical_analysis", {}),
            sentiment_analysis=analysis_result.get("sentiment_analysis", {}),
            news_headlines=analysis_result.get("news_headlines", []),
            chart=analysis_result.get("chart", ""),
            data_points=analysis_result.get("data_points", 0),
            period=analysis_result.get("period", request.period),
            interval=analysis_result.get("interval", request.interval)
        )
        
        # Store result in database (background task)
        background_tasks.add_task(store_analysis_result, result_obj.dict())
        
        return analysis_result
        
    except Exception as e:
        logging.error(f"Error in analyze_forex_pair: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.get("/fx/history")
async def get_analysis_history(limit: int = 10, pair: Optional[str] = None):
    """Get historical analysis results"""
    try:
        query = {}
        if pair:
            query["pair"] = pair
            
        results = await db.fx_analyses.find(query).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Remove chart data for history view to reduce response size
        for result in results:
            if "chart" in result:
                result["chart"] = ""
                
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        logging.error(f"Error getting analysis history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@api_router.get("/fx/pairs")
async def get_supported_pairs():
    """Get list of supported forex pairs"""
    pairs = [
        {"symbol": "EURUSD=X", "name": "EUR/USD", "description": "Euro to US Dollar"},
        {"symbol": "GBPUSD=X", "name": "GBP/USD", "description": "British Pound to US Dollar"},
        {"symbol": "USDJPY=X", "name": "USD/JPY", "description": "US Dollar to Japanese Yen"},
        {"symbol": "AUDUSD=X", "name": "AUD/USD", "description": "Australian Dollar to US Dollar"},
        {"symbol": "USDCAD=X", "name": "USD/CAD", "description": "US Dollar to Canadian Dollar"},
        {"symbol": "USDCHF=X", "name": "USD/CHF", "description": "US Dollar to Swiss Franc"},
        {"symbol": "EURGBP=X", "name": "EUR/GBP", "description": "Euro to British Pound"},
        {"symbol": "EURJPY=X", "name": "EUR/JPY", "description": "Euro to Japanese Yen"}
    ]
    return {"pairs": pairs}

@api_router.get("/fx/news")
async def get_forex_news():
    """Get latest forex-related news"""
    try:
        news_headlines = await fx_analyzer.fetch_news()
        sentiment_data = await fx_analyzer.analyze_sentiment(news_headlines)
        
        return {
            "headlines": news_headlines,
            "sentiment": sentiment_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting forex news: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get news: {str(e)}")

async def store_analysis_result(result_data: dict):
    """Background task to store analysis result in database"""
    try:
        await db.fx_analyses.insert_one(result_data)
    except Exception as e:
        logging.error(f"Error storing analysis result: {e}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.on_event("startup")
async def startup_event():
    logger.info("FX Analyzer API starting up...")
    # Create database indexes
    try:
        await db.fx_analyses.create_index("created_at")
        await db.fx_analyses.create_index("pair")
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Error creating database indexes: {e}")