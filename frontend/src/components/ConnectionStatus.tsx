import React from 'react';
import { ConnectionStatusType } from '../types/types';

interface ConnectionStatusProps {
  status: ConnectionStatusType;
  onReconnect: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ status, onReconnect }) => {
  const statusStyles = {
    connecting: 'bg-yellow-500 text-white',
    connected: 'bg-green-500 text-white',
    disconnected: 'bg-red-500 text-white',
    error: 'bg-red-700 text-white'
  };

  const statusIcons = {
    connecting: '🔄',
    connected: '✅',
    disconnected: '❌',
    error: '⚠️'
  };

  return (
    <div className={`p-2 rounded flex justify-between items-center ${statusStyles[status]}`}>
      <span>
        {statusIcons[status]} Connection Status: {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
      {(status === 'disconnected' || status === 'error') && (
        <button 
          onClick={onReconnect} 
          className="bg-white text-black px-2 py-1 rounded hover:bg-gray-200"
        >
          Reconnect
        </button>
      )}
    </div>
  );
};

export default ConnectionStatus;