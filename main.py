from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import uuid
from typing import Dict, List, Any, Optional
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

# Store active connections and chat history
chat_histories: Dict[str, List[Dict[str, Any]]] = {}
sentiment_analyzer = SentimentAnalyzer()

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if client_id not in chat_histories:
            chat_histories[client_id] = []

    def disconnect(self, client_id: str) -> None:
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: str, client_id: str) -> None:
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": f"An error occurred: {str(exc)}"}
    )

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    await manager.connect(websocket, client_id)
    try:
        while True:
            data: str = await websocket.receive_text()
            message_data: Dict[str, Any] = json.loads(data)
            
            # Add message to chat history
            chat_histories[client_id].append(message_data)
            
            # Format conversation for sentiment analysis
            conversation: str = "\n".join([
                f"{'Customer' if msg['role'] == 'customer' else 'Agent'}: {msg['content']}" 
                for msg in chat_histories[client_id]
            ])
            
            # Analyze sentiment
            sentiment_data: SentimentData = sentiment_analyzer.analyze_sentiment(conversation)
            
            # Get suggestions if sentiment is negative
            suggestions: List[str] = sentiment_analyzer.get_suggestions(conversation, sentiment_data)
            
            # Send message to all connections with the same client_id
            response: Dict[str, Any] = {
                "message": message_data,
                "sentiment": sentiment_data,
                "suggestions": suggestions
            }
            
            await manager.send_message(json.dumps(response), client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.post("/api/sentiment")
async def analyze_sentiment(conversation: ConversationInput) -> Dict[str, Any]:
    convo_text: str = conversation.text
    sentiment_data: SentimentData = sentiment_analyzer.analyze_sentiment(convo_text)
    suggestions: List[str] = sentiment_analyzer.get_suggestions(convo_text, sentiment_data)
    return {"sentiment": sentiment_data, "suggestions": suggestions}

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Customer Support Sentiment Analysis API"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
