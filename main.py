from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from pydantic import BaseModel
from sentiment_analyzer import SentimentAnalyzer, SentimentData

class ConversationInput(BaseModel):
    text: str

class MentorshipResponse(BaseModel):
    sentiment: SentimentData
    suggestions: List[str]

# Create a FastAPI instance
app = FastAPI()

# Add app middleware to allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/mentor")
async def analyze_sentiment(conversation: ConversationInput) -> MentorshipResponse:
    """
    Analyze sentiment and provide suggestions for customer support conversations.
    """
    conv_text: str = conversation.text
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_data: SentimentData = sentiment_analyzer.analyze_sentiment(conv_text)
    suggestions: List[str] = sentiment_analyzer.get_suggestions(conv_text, sentiment_data)
    return MentorshipResponse(sentiment=sentiment_data, suggestions=suggestions)

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint to provide information about the API."""
    return {"message": "Customer Support Sentiment Analysis API"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}
