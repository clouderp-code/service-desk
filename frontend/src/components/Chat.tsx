import React, { useState, useEffect, useRef } from 'react';

interface Message {
  content: string;
  timestamp: string;
  isUser: boolean;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const websocket = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const connectWebSocket = () => {
      websocket.current = new WebSocket('ws://localhost:8000/api/chat/ws');

      websocket.current.onopen = () => {
        console.log('Connected to chat server');
        setIsConnected(true);
      };

      websocket.current.onmessage = (event) => {
        console.log('Received message:', event.data); // Debug log
        const response = JSON.parse(event.data);
        setIsLoading(false);

        if (response.error) {
          console.error('Error:', response.error);
          // Add error message to chat
          setMessages(prev => [...prev, {
            content: `Error: ${response.error}`,
            timestamp: response.timestamp || new Date().toLocaleString(),
            isUser: false
          }]);
        } else {
          setMessages(prev => [...prev, {
            content: response.response,
            timestamp: response.timestamp || new Date().toLocaleString(),
            isUser: false
          }]);
        }
      };

      websocket.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setIsLoading(false);
      };

      websocket.current.onclose = () => {
        console.log('Disconnected from chat server');
        setIsConnected(false);
        setIsLoading(false);
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();

    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !websocket.current || !isConnected) return;

    setIsLoading(true);
    // Add user message to chat
    setMessages(prev => [...prev, {
      content: inputMessage,
      timestamp: new Date().toLocaleString(),
      isUser: true
    }]);

    // Send message to server
    websocket.current.send(JSON.stringify({ content: inputMessage }));
    setInputMessage('');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="p-4 bg-white shadow">
        <h1 className="text-xl font-semibold">Chat Assistant</h1>
        <div className={`text-sm ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.isUser
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800 shadow'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              <div className="text-xs mt-1 opacity-75">
                {message.timestamp}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 rounded-lg p-3 animate-pulse">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} className="p-4 bg-white shadow">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={!isConnected || isLoading}
          />
          <button
            type="submit"
            className={`px-4 py-2 rounded-lg ${
              isConnected && !isLoading
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            disabled={!isConnected || isLoading}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat; 