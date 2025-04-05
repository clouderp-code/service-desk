import React, { useState, useEffect, useCallback } from 'react';

const Chat: React.FC = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Create a direct send function
  const sendWebSocketMessage = useCallback((ws: WebSocket, text: string) => {
    const payload = JSON.stringify({ message: text });
    console.log('Sending exact payload:', payload);
    ws.send(payload);
  }, []);

  useEffect(() => {
    const wsUrl = `ws://${window.location.hostname}:8000/api/chat/ws`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('Connected to WebSocket');
    };

    websocket.onmessage = (event) => {
      console.log('Received:', event.data);
      const data = JSON.parse(event.data);
      if (data.error) {
        setError(data.error);
      } else if (data.response) {
        setMessages(prev => [...prev, `AI: ${data.response}`]);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error');
    };

    setWs(websocket);

    return () => websocket.close();
  }, []);

  const handleSendMessage = (event: React.FormEvent) => {
    event.preventDefault();
    if (message.trim() && ws && ws.readyState === WebSocket.OPEN) {
      try {
        // Send directly without any intermediate steps
        sendWebSocketMessage(ws, message.trim());
        setMessages(prev => [...prev, `You: ${message}`]);
        setMessage('');
        setError(null);
      } catch (err: any) {
        setError(`Error: ${err?.message || 'Unknown error'}`);
      }
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 p-4 overflow-y-auto">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div key={index} className="p-2">{msg}</div>
          ))}
        </div>
      </div>
      <form onSubmit={handleSendMessage} className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message here..."
            className="flex-1 p-2 border rounded"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat; 