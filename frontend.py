import streamlit as st
import websocket
import json
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Literal, cast

# Set page config
st.set_page_config(
    page_title="Support Chat with Sentiment Analysis",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, Any]] = []
if "client_id" not in st.session_state:
    st.session_state.client_id: str = str(uuid.uuid4())
if "role" not in st.session_state:
    st.session_state.role: Optional[str] = None
if "ws" not in st.session_state:
    st.session_state.ws: Optional[websocket.WebSocketApp] = None
if "sentiment" not in st.session_state:
    st.session_state.sentiment: Dict[str, Union[str, float]] = {
        "sentiment": "neutral", 
        "score": 0.0, 
        "reason": "No messages yet"
    }
if "suggestions" not in st.session_state:
    st.session_state.suggestions: List[str] = []
if "connection_status" not in st.session_state:
    st.session_state.connection_status: str = "disconnected"

# Type for role selection
RoleType = Literal["customer", "support agent"]

# WebSocket message handler
def on_message(ws: websocket.WebSocketApp, message: str) -> None:
    try:
        data: Dict[str, Any] = json.loads(message)
        
        # Add message to chat if not already there
        new_message: Dict[str, Any] = data["message"]
        message_exists: bool = any(
            msg["id"] == new_message["id"] 
            for msg in st.session_state.messages
        )
        
        if not message_exists:
            st.session_state.messages.append(new_message)
        
        # Update sentiment and suggestions
        st.session_state.sentiment = data["sentiment"]
        st.session_state.suggestions = data["suggestions"]
        
        # Force a rerun to update the UI
        st.rerun()
    except Exception as e:
        st.error(f"Error processing message: {e}")

def on_error(ws: websocket.WebSocketApp, error: Exception) -> None:
    st.session_state.connection_status = "error"
    print(f"WebSocket Error: {error}")
    st.error(f"WebSocket Error: {error}")

def on_close(ws: websocket.WebSocketApp, close_status_code: Optional[int], close_reason: Optional[str]) -> None:
    st.session_state.connection_status = "disconnected"
    print("WebSocket connection closed")

def on_open(ws: websocket.WebSocketApp) -> None:
    st.session_state.connection_status = "connected"
    print("Connected to chat server")

# Initialize WebSocket connection
def setup_websocket() -> None:
    if st.session_state.ws is None or st.session_state.connection_status != "connected":
        try:
            ws = websocket.WebSocketApp(
                f"ws://localhost:8000/ws/{st.session_state.client_id}",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()
            st.session_state.ws = ws
            time.sleep(1)  # Give the connection time to establish
        except Exception as e:
            st.error(f"Error establishing WebSocket connection: {e}")

# Set up the UI
st.title("Customer Support Chat with Sentiment Analysis")

# Connection status indicator
if st.session_state.connection_status == "connected":
    st.success("✅ Connected to chat server")
elif st.session_state.connection_status == "error":
    st.error("❌ Connection error - Check if the server is running")
    if st.button("Reconnect"):
        st.session_state.connection_status = "disconnected"
        st.session_state.ws = None
        setup_websocket()
        st.rerun()
else:
    st.warning("⚠️ Not connected - Attempting to connect...")
    setup_websocket()

# Role selection sidebar
with st.sidebar:
    st.header("Settings")
    role: str = st.radio("Select your role:", ("Customer", "Support Agent"))
    st.session_state.role = role.lower()
    
    st.header("Sentiment Analysis")
    sentiment: Dict[str, Union[str, float]] = st.session_state.sentiment
    
    # Display sentiment with colored indicators
    sentiment_color: str = {
        "positive": "green",
        "neutral": "gray",
        "negative": "red"
    }.get(cast(str, sentiment["sentiment"]), "gray")
    
    st.markdown(f"**Current Sentiment:** <span style='color:{sentiment_color}'>{cast(str, sentiment['sentiment']).upper()}</span>", unsafe_allow_html=True)
    
    # Use a more intuitive progress bar
    score_value = float(cast(float, sentiment["score"]))
    normalized_score = (score_value + 1) / 2  # Convert -1 to 1 range to 0 to 1
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.write("😠")
    with col2:
        st.progress(normalized_score)
    with col3:
        st.write("😊")
        
    st.text(f"Score: {score_value:.2f}")
    
    with st.expander("Analysis Reason"):
        st.write(sentiment["reason"])
    
    # Show suggestions only for the support agent
    if st.session_state.role == "support agent" and st.session_state.suggestions:
        st.header("💡 Improvement Suggestions")
        for i, suggestion in enumerate(st.session_state.suggestions):
            with st.container(border=True):
                st.markdown(f"**Suggestion {i+1}:** {suggestion}")

# Chat interface with more styling
chat_col, info_col = st.columns([4, 1])

with chat_col:
    # Display chat messages
    st.markdown("### Conversation")
    
    if not st.session_state.messages:
        st.info("No messages yet. Start the conversation!")
    
    for msg in st.session_state.messages:
        is_customer = msg["role"] == "customer"
        with st.chat_message(
            "user" if is_customer else "assistant", 
            avatar="👤" if is_customer else "🧑‍💼"
        ):
            st.write(f"{msg['content']}")
            st.caption(f"{msg['timestamp']}")
    
    # Chat input
    if st.session_state.role:
        if st.session_state.connection_status == "connected":
            # Only show input if a role is selected and connected
            prompt: Optional[str] = st.chat_input(f"Message as {st.session_state.role.capitalize()}")
            if prompt:
                # Create message
                message: Dict[str, str] = {
                    "id": str(uuid.uuid4()),
                    "role": st.session_state.role,
                    "content": prompt,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                
                # Send message via WebSocket
                if st.session_state.ws:
                    try:
                        st.session_state.ws.send(json.dumps(message))
                    except Exception as e:
                        st.error(f"Error sending message: {e}")
                        st.session_state.connection_status = "error"
        else:
            st.error("Cannot send messages while disconnected. Check the server connection.")
    else:
        st.info("Please select a role from the sidebar to start chatting")

with info_col:
    st.markdown("### About")
    st.markdown("""
    This customer support messenger features real-time sentiment analysis powered by AI.
    
    **Features:**
    - Real-time chat between customer and agent
    - Sentiment analysis of the conversation
    - AI-powered suggestions for improving negative interactions
    - Visual sentiment indicators
    """)
