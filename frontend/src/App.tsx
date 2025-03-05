import React, { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatMessage from './components/ChatMessage';
import SentimentAnalyzer from './components/SentimentAnalyzer';
import ConnectionStatus from './components/ConnectionStatus';
import { Message, SentimentData, ChatResponse } from './types/types';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [role, setRole] = useState<'customer' | 'support agent'>('customer');
  const [clientId] = useState(uuidv4());
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [sentiment, setSentiment] = useState<SentimentData>({
    sentiment: 'neutral',
    score: 0,
    reason: 'No messages yet'
  });
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const connectWebSocket = useCallback(() => {
    setConnectionStatus('connecting');
    const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    ws.onopen = () => {
      setConnectionStatus('connected');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data: ChatResponse = JSON.parse(event.data);
        
        // Add new message if not already exists
        setMessages(prevMessages => {
          const messageExists = prevMessages.some(msg => msg.id === data.message.id);
          return messageExists 
            ? prevMessages 
            : [...prevMessages, data.message];
        });

        // Update sentiment and suggestions
        setSentiment(data.sentiment);
        setSuggestions(data.suggestions);
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    ws.onerror = () => {
      setConnectionStatus('error');
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
    };

    return ws;
  }, [clientId]);

  useEffect(() => {
    const ws = connectWebSocket();
    return () => {
      ws.close();
    };
  }, [connectWebSocket]);

  const sendMessage = () => {
    if (inputMessage.trim() && socket && socket.readyState === WebSocket.OPEN) {
      const message: Message = {
        id: uuidv4(),
        role: role,
        content: inputMessage,
        timestamp: new Date().toLocaleTimeString()
      };

      socket.send(JSON.stringify(message));
      setInputMessage('');
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <ConnectionStatus 
        status={connectionStatus} 
        onReconnect={connectWebSocket} 
      />

      <div className="flex flex-grow overflow-hidden">
        <div className="w-2/3 pr-4 flex flex-col">
          <div className="flex-grow overflow-y-auto mb-4">
            {messages.map(message => (
              <ChatMessage key={message.id} message={message} />
            ))}
          </div>

          <div className="mt-auto">
            <div className="flex">
              <select 
                value={role} 
                onChange={(e) => setRole(e.target.value as 'customer' | 'support agent')}
                className="mr-2 p-2 border rounded"
              >
                <option value="customer">Customer</option>
                <option value="support agent">Support Agent</option>
              </select>
              <input 
                type="text" 
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                className="flex-grow p-2 border rounded mr-2"
              />
              <button 
                onClick={sendMessage}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        <div className="w-1/3 border-l pl-4">
          <SentimentAnalyzer 
            sentiment={sentiment} 
            suggestions={suggestions}
            role={role}
          />
        </div>
      </div>
    </div>
  );
};

export default App;