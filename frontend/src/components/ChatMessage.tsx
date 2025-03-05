import React from 'react';
import { Message } from '../types/types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isCustomer = message.role === 'customer';

  return (
    <div className={`flex ${isCustomer ? 'justify-start' : 'justify-end'} mb-4`}>
      <div 
        className={`
          max-w-[70%] p-3 rounded-lg shadow-md
          ${isCustomer 
            ? 'bg-blue-100 text-blue-800' 
            : 'bg-green-100 text-green-800'
          }
        `}
      >
        <div className="text-sm font-semibold mb-1">
          {isCustomer ? '👤 Customer' : '🧑‍💼 Support Agent'}
        </div>
        <p>{message.content}</p>
        <div className="text-xs text-gray-500 mt-1 text-right">
          {message.timestamp}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;