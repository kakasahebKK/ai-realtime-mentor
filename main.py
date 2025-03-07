from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from pydantic import BaseModel
from sentiment_analyzer import SentimentAnalyzer, SentimentData

class ConversationInput(BaseModel):
    text: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/sentiment")
async def analyze_sentiment(conversation: ConversationInput) -> Dict[str, Any]:
    convo_text: str = conversation.text
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_data: SentimentData = sentiment_analyzer.analyze_sentiment(convo_text)
    suggestions: List[str] = sentiment_analyzer.get_suggestions(convo_text, sentiment_data)
    return {"sentiment": sentiment_data, "suggestions": suggestions}

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Customer Support Sentiment Analysis API"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
